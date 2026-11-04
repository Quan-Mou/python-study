# 聊天接口：SSE 流式对话 + 历史记录查询
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.repositories.conversation_repo import ConversationRepository
from app.repositories.message_repo import MessageRepository
from app.schemas.chat import ChatRequest
from app.services.chat_service import ChatService

# prefix="/chat"：本文件路由都加 /chat 前缀
router = APIRouter(prefix="/chat", tags=["聊天"])


@router.post("")
async def chat(
    data: ChatRequest,
    request: Request,
    user: User = Depends(get_current_user),  # 必须先登录
    db: AsyncSession = Depends(get_db),
):
    # 确定 thread_id：没传就新生成一个（uuid.hex 是 32 位十六进制字符串，唯一）
    thread_id = data.thread_id or uuid.uuid4().hex

    # 用请求级 session 保存会话 + 用户消息（这些要在开始流式前落库）
    conv_repo = ConversationRepository(db)
    msg_repo = MessageRepository(db)

    # 按 thread_id 找会话；不存在则新建（新会话标题取首条消息前 30 字）
    conv = await conv_repo.get_by_thread_id(thread_id)
    if conv is None:
        conv = await conv_repo.create(user.id, thread_id, title=data.content[:30])

    # 保存用户这条消息
    await msg_repo.create(conv.id, "user", data.content)

    # 从 app.state 取出编译好的 Agent（lifespan 里创建的）
    agent = request.app.state.agent

    # 组装流式服务，返回 SSE 响应
    service = ChatService(agent)
    return StreamingResponse(
        # 生成器逐 token yield SSE 事件；generator 里会再开独立 session 保存 assistant 消息
        service.stream_with_save(
            thread_id, conv.id, data.content, request.app.state.session_factory
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",       # 禁止缓存，确保实时
            "X-Accel-Buffering": "no",         # 关闭反向代理缓冲（Nginx）
        },
    )


@router.get("/history/{thread_id}")
async def history(
    thread_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # 按 thread_id 找会话，校验是否属于当前用户（防止越权读别人的对话）
    conv = await ConversationRepository(db).get_by_thread_id(thread_id)
    if conv is None or conv.user_id != user.id:
        raise HTTPException(404, "会话不存在")

    # 返回该会话的全部消息
    msgs = await MessageRepository(db).list_by_conversation(conv.id)
    return [
        {"role": m.role, "content": m.content, "created_at": m.created_at.isoformat()}
        for m in msgs
    ]

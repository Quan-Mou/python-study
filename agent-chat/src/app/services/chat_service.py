# 聊天业务层：调 LangGraph Agent 做 SSE 流式输出，并在流式结束后保存 assistant 消息
import json
from collections.abc import AsyncIterator

from langchain_core.messages import AIMessageChunk, HumanMessage

from app.repositories.message_repo import MessageRepository


class ChatService:
    def __init__(self, agent):
        # 注入编译好的 LangGraph Agent（CompiledStateGraph）
        self.agent = agent

    async def stream_with_save(
        self, thread_id: str, conversation_id: int, content: str, session_factory
    ) -> AsyncIterator[str]:
        """流式产出 SSE 事件，并在结束后把 assistant 完整回复写入数据库。

        参数：
          thread_id        —— LangGraph 线程 id（checkpointer 据此保存/恢复状态）
          conversation_id  —— 业务库 conversations.id（保存 assistant 消息用）
          content          —— 用户本次发送的内容
          session_factory  —— 异步 session 工厂（流式阶段独立开连接，不占用请求的 session）
        """
        # 把 dict 编码成一条 SSE 消息（ensure_ascii=False 保证中文原样输出）
        def sse(payload: dict) -> str:
            return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

        # checkpointer 用 thread_id 区分不同会话，续聊传相同 id 即恢复上下文
        config = {"configurable": {"thread_id": thread_id}}

        # 累积完整回复，结束后一次性落库
        full_text = ""

        # astream 异步流式执行图；stream_mode="messages" 返回消息级增量
        # 每项是 (消息块, 元数据) 元组，AI 消息块是 AIMessageChunk（token 级文本增量）
        async for chunk in self.agent.astream(
            {"messages": [HumanMessage(content=content)]},
            config=config,
            stream_mode="messages",
        ):
            msg_chunk, _meta = chunk

            # 只处理模型产生的 AI 消息块
            if not isinstance(msg_chunk, AIMessageChunk):
                continue

            # 有文本内容 → token 增量，累积并流式下发
            if msg_chunk.content:
                full_text += msg_chunk.content
                yield sse({"type": "token", "content": msg_chunk.content})

            # 带 tool_calls → 模型要调工具，提示前端
            if msg_chunk.tool_calls:
                for tc in msg_chunk.tool_calls:
                    if tc.get("name"):
                        yield sse({"type": "tool", "name": tc["name"]})

        # 流式结束后，把 assistant 完整回复写入业务库（用独立 session，避免长连接占用）
        async with session_factory() as db:
            await MessageRepository(db).create(conversation_id, "assistant", full_text)

        # 结束事件：附完整回复，前端可据此停止 loading
        yield sse({"type": "done", "content": full_text})

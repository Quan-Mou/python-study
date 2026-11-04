# 消息数据访问层
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.message import Message


class MessageRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, conversation_id: int, role: str, content: str) -> Message:
        # 插入一条消息记录（role：user/assistant/tool）
        msg = Message(conversation_id=conversation_id, role=role, content=content)
        self.db.add(msg)
        await self.db.commit()
        await self.db.refresh(msg)
        return msg

    async def list_by_conversation(self, conversation_id: int) -> list[Message]:
        # 按会话 id 查全部消息，按 id 升序（即时间先后）
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.id)
        )
        return list(result.scalars().all())

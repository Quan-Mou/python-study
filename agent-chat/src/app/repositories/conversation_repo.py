# 会话数据访问层
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Conversation


class ConversationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_thread_id(self, thread_id: str) -> Conversation | None:
        # 按 LangGraph thread_id 查会话（续聊时用它找回业务会话）
        result = await self.db.execute(
            select(Conversation).where(Conversation.thread_id == thread_id)
        )
        return result.scalar_one_or_none()

    async def create(
        self, user_id: int, thread_id: str, title: str | None = None
    ) -> Conversation:
        conv = Conversation(user_id=user_id, thread_id=thread_id, title=title)
        self.db.add(conv)
        await self.db.commit()
        await self.db.refresh(conv)
        return conv

# 会话表模型：一次对话（一个 thread）对应一行
import datetime

from sqlalchemy import String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # 属于哪个用户（逻辑外键，指向 users.id）
    user_id: Mapped[int] = mapped_column(index=True)
    # 会话标题：可空，通常取首条消息前若干字
    title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    # LangGraph 的 thread_id：checkpointer 用它保存/恢复工作流状态，业务表与它一一对应
    thread_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
    # onupdate：每次 UPDATE 时自动刷新为当前时间
    updated_at: Mapped[datetime.datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

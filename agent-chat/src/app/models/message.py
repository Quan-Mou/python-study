# 消息表模型：会话里的一条条对话记录
import datetime

from sqlalchemy import String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # 属于哪个会话（逻辑外键，指向 conversations.id）
    conversation_id: Mapped[int] = mapped_column(index=True)
    # 角色：user（用户）/ assistant（模型）/ tool（工具）
    role: Mapped[str] = mapped_column(String(20))
    # 消息内容：用 Text 存长文本
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())

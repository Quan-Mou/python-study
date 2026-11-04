# 聊天相关的请求模型
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    # 用户这次要发的内容
    content: str = Field(min_length=1)
    # 可选：续聊时传上次的 thread_id；不传则新建一个会话
    thread_id: str | None = None

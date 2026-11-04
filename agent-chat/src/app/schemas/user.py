# 用户相关的请求/响应模型（DTO / VO）
from pydantic import BaseModel, ConfigDict, Field


class RegisterRequest(BaseModel):
    # 请求体：注册。Field 定义长度约束，FastAPI 自动做 422 校验
    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=6, max_length=20)
    email: str | None = None


class LoginRequest(BaseModel):
    # 请求体：登录
    username: str
    password: str


class TokenResponse(BaseModel):
    # 响应：登录成功后返回的 token
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    # 响应：用户信息。from_attributes 允许直接从一个 ORM User 对象取值
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str | None

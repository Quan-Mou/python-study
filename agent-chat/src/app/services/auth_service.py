# 认证业务层：注册、登录
from fastapi import HTTPException

from app.core.security import create_access_token, hash_password, verify_password
from app.repositories.user_repo import UserRepository
from app.schemas.user import LoginRequest, RegisterRequest, TokenResponse, UserResponse


class AuthService:
    def __init__(self, repo: UserRepository):
        # 注入用户仓库
        self.repo = repo

    async def register(self, data: RegisterRequest) -> UserResponse:
        # 用户名查重：已存在 → 400
        if await self.repo.get_by_username(data.username) is not None:
            raise HTTPException(400, "用户名已存在")

        # 密码哈希后入库（明文只在这一行出现，随后即被丢弃）
        hashed = hash_password(data.password)
        user = await self.repo.create(data.username, hashed, data.email)

        # ORM 对象 → 响应模型
        return UserResponse.model_validate(user)

    async def login(self, data: LoginRequest) -> TokenResponse:
        user = await self.repo.get_by_username(data.username)

        # 用户不存在或密码不对 → 统一提示（不区分"用户名错"还是"密码错"，避免被探测账号是否存在）
        if user is None or not verify_password(data.password, user.hashed_password):
            raise HTTPException(400, "用户名或密码错误")

        # 签发 token 并返回
        return TokenResponse(access_token=create_access_token(user.id, user.username))

# 认证接口：注册 / 登录 / 查看当前用户
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.schemas.user import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from app.services.auth_service import AuthService

# prefix="/auth"：本文件所有路由都加 /auth 前缀（再经 router 挂 /api → /api/auth/...）
router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register", response_model=UserResponse)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # 组装 仓库 + 服务，交给服务层处理业务
    return await AuthService(UserRepository(db)).register(data)


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    # 登录成功返回 access_token
    return await AuthService(UserRepository(db)).login(data)


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    # get_current_user 已经校验并查出了用户，直接返回即可
    return current_user

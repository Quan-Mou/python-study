# 路由汇总：把 auth、chat 子路由统一挂到一个 router 上
from fastapi import APIRouter

from app.api import auth, chat

router = APIRouter()

# include_router 把各子模块的路由并进来（tags 用于 Swagger 文档分组）
router.include_router(auth.router)
router.include_router(chat.router)

# 路由汇总
from fastapi import APIRouter

from app.api import users, auth

router= APIRouter()

router.include_router(users.router)
router.include_router(auth.router)


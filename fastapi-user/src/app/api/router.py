# 路由汇总
from fastapi import APIRouter

from app.api import users

router= APIRouter()

router.include_router(users.router)


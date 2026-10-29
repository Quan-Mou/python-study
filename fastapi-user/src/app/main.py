from fastapi import FastAPI

from app.api.router import router
from app.core.deps import engine
from app.models.users import Base

app = FastAPI(title="fastapi-demo")

# 启动时按 models 自动建表（学习项目够用；生产环境应使用 alembic 迁移）
Base.metadata.create_all(engine)

# 统一挂载汇总路由，加 /v1 前缀 → /v1/users/*
app.include_router(router, prefix="/v1")

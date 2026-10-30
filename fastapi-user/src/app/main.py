import logging
import time

from fastapi import FastAPI

from app.api.router import router
from app.core.deps import engine
from app.models.users import Base
from fastapi.requests import Request

from app.core.exceptions import registry_exception_handlers

app = FastAPI(title="fastapi-demo")

# 启动时按 models 自动建表（学习项目够用；生产环境应使用 alembic 迁移）
Base.metadata.create_all(engine)

# 注册异常
registry_exception_handlers(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


#  中间件：py中的中间件有点想java中的拦截器，或者aop
@app.middleware("http")
async def log_request(request:Request, call_next):
    start_time = time.perf_counter()

    response = await call_next(request)

    duration = time.perf_counter() - start_time

    logger.info(
        request.method,
        request.url,
        response.status_code,
        duration,
    )
    return response


# 统一挂载汇总路由，加 /v1 前缀 → /v1/users/*
app.include_router(router, prefix="/v1")
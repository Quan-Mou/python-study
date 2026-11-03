from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI


# 在接口中使用共享客户端

@asynccontextmanager
async def lifespan(app:FastAPI):
    print("fastapi正在启动")
    app.state.http_client = httpx.AsyncClient(timeout=10)

    yield
    # 应用关闭阶段
    await app.state.http_client.aclose()


app  = FastAPI(lifespan=lifespan)

# 导入包含路由的模块：模块顶层的 @app.get(...) 装饰器在导入时执行，路由才被注册
# （必须放在 app 创建之后；导入了谁，谁的路由才会生效）
from . import use_client  # noqa: E402,F401





from fastapi import FastAPI, Request

from .life_span import app  # 相对导入，保证从任何目录以包方式启动都能找到


# 该模块被 life_span.py 导入时，下面的装饰器才执行，路由才注册进 app
@app.get("/external")
async def external_api(request: Request):
    # 从当前请求对应的 app 实例上取 lifespan 创建的共享 client
    client = request.app.state.http_client
    response = await client.get(
        "https://httpbin.org/get"
    )

    response.raise_for_status()

    return response.json()

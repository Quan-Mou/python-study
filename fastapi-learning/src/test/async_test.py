import pytest
from httpx import ASGITransport, AsyncClient

from .main import app

#  异步接口测试

@pytest.mark.asyncio
async def test_async_api():
    # 直接把请求发送到 ASGITransport：请求不经过网络，直达 app 的 ASGI 入口
    transport = ASGITransport(app)

    # 异步测试 Http 客户端
    async with AsyncClient(
        transport=transport,
        base_url="http://testserver"  # 占位符：ASGITransport 不走网络，写合法的假域名即可
    ) as client:
        response = await client.get("/async")  # main.py 里的 async def 路由

        assert response.status_code == 200
        assert response.json() == {"message": "Hello Async"}

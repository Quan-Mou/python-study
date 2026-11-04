# 测试公共夹具：注入假模型 + 内存 SQLite，避免碰真 LLM 和真 MySQL
import pytest
from httpx import ASGITransport, AsyncClient
from langchain.agents import create_agent
from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langgraph.checkpoint.memory import InMemorySaver
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.main import create_app
from app.models.base import Base


@pytest.fixture
async def client():
    # 1. 假模型：对任何输入都返回固定答复，且不调用工具
    fake_model = FakeListChatModel(responses=["你好，我是测试助手。"])

    # 2. 假 agent：内存 checkpointer（不落盘），工具传空列表
    fake_agent = create_agent(fake_model, tools=[], checkpointer=InMemorySaver())

    # 3. 内存 SQLite：每个测试独立，互不污染（aiosqlite 内存库）
    engine = create_async_engine("sqlite+aiosqlite://")
    async with engine.begin() as conn:
        # 建表
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    # 4. 用注入的假依赖创建 app
    app = create_app(agent=fake_agent, session_factory=session_factory)

    # 5. 手动进入 lifespan 让 app.state 就绪，再用 AsyncClient 通过 ASGI 直接调
    async with app.router.lifespan_context(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            yield c

    # 6. 清理：关闭内存库
    await engine.dispose()


@pytest.fixture
async def token(client):
    """注册一个用户并登录，返回 access_token（后续请求带它做认证）。"""
    # 注册
    resp = await client.post(
        "/api/auth/register",
        json={"username": "alice", "password": "secret123"},
    )
    assert resp.status_code == 200
    # 登录拿 token
    resp = await client.post(
        "/api/auth/login",
        json={"username": "alice", "password": "secret123"},
    )
    assert resp.status_code == 200
    return resp.json()["access_token"]

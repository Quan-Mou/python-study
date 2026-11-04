# 应用入口：组装 FastAPI app（工厂模式，便于测试注入假依赖）
from contextlib import asynccontextmanager

import aiosqlite
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from app.agent.graph import build_agent
from app.api.router import router
from app.core.database import AsyncSessionLocal, engine, get_db
from app.models.base import Base


def create_app(agent=None, session_factory=None) -> FastAPI:
    """工厂：创建 FastAPI 应用。

    参数：
      agent            —— 注入编译好的 LangGraph Agent（测试传假模型 agent，生产传 None）
      session_factory  —— 注入异步 session 工厂（测试传内存 SQLite 工厂，生产传 None）
    生产环境两者都传 None，由 lifespan 构建真实依赖。
    """
    # 若没注入 session 工厂，用全局 MySQL 工厂
    if session_factory is None:
        session_factory = AsyncSessionLocal

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # 生产（未注入 session_factory）才在真实 MySQL 上建表；
        # 测试注入了内存 SQLite 工厂，表由 conftest 建好，这里跳过（否则会连真 MySQL）
        if session_factory is None:
            async with engine.begin() as conn:
                # run_sync 让同步的 create_all 跑在线程里，不阻塞事件循环
                await conn.run_sync(Base.metadata.create_all)

        # 若测试已注入 agent，则不重建；否则构建真实 agent（真实模型 + SQLite 持久化）
        if app.state.agent is None:
            # 手动打开 SQLite 连接并构造 checkpointer——连接必须保持打开到应用关闭，
            # 所以这里把它存到 app.state，shutdown 时再 close
            cp_conn = await aiosqlite.connect("checkpoints.sqlite")
            checkpointer = AsyncSqliteSaver(cp_conn)
            app.state.agent = build_agent(checkpointer=checkpointer)
            app.state._checkpointer_conn = cp_conn

        yield  # 应用正常运行期间停在这里

        # 关闭：释放 checkpointer 的 SQLite 连接
        cp_conn = getattr(app.state, "_checkpointer_conn", None)
        if cp_conn is not None:
            await cp_conn.close()

    app = FastAPI(title="agent-chat", lifespan=lifespan)

    # 把注入的依赖挂到 app.state，路由里通过 request.app.state 取用
    app.state.agent = agent
    app.state.session_factory = session_factory

    # 若测试注入了 session_factory，把 get_db 依赖也换成它——
    # 这样所有 Depends(get_db)（含 get_current_user 内部）都走注入的内存库，不碰真 MySQL
    if session_factory is not None:

        async def _override_get_db():
            # 覆盖版依赖：用注入的工厂开独立 session
            async with session_factory() as session:
                yield session

        app.dependency_overrides[get_db] = _override_get_db

    # 跨域中间件：学习期放开所有来源
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 统一挂载汇总路由，加 /api 前缀 → /api/auth/*、/api/chat/*
    app.include_router(router, prefix="/api")

    # 健康检查
    @app.get("/api/health")
    async def health():
        return {"status": "ok"}

    return app


# 模块级实例：uvicorn app.main:app 直接用这个
app = create_app()

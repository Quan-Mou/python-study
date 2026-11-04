# 异步数据库基础设施：engine + session 工厂 + 依赖注入
from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

# 异步引擎：所有 DB 操作都通过它拿连接。pool_pre_ping 使用前先探测连接是否存活
# echo=False 不打印 SQL（学习排查时可临时改 True）
engine = create_async_engine(settings.database_url, echo=False, pool_pre_ping=True)

# async session 工厂：每处调用 new 一个独立 session，互不共享
# expire_on_commit=False：commit 后对象属性仍可访问，异步下更友好
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncIterator[AsyncSession]:
    # FastAPI 依赖：yield 出一个 session，请求结束自动关闭（async with 保证资源释放）
    async with AsyncSessionLocal() as session:
        yield session

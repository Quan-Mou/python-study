# 用户数据访问层（DAO）：只负责 SQL，不含业务逻辑
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        # 注入一个 session，本仓库所有操作都在这条连接上进行
        self.db = db

    async def get_by_username(self, username: str) -> User | None:
        # 按用户名查；用户名唯一，用 scalar_one_or_none 取单条或 None
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> User | None:
        # 按主键查
        return await self.db.get(User, user_id)

    async def create(self, username: str, hashed_password: str, email: str | None) -> User:
        # 构造 ORM 对象 → 加入会话 → 提交 → 刷新拿到自增 id
        user = User(username=username, hashed_password=hashed_password, email=email)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

# 用户表模型
import datetime

from sqlalchemy import String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class User(Base):
    # 表名
    __tablename__ = "users"

    # 主键，自增
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # 用户名：唯一 + 索引（登录按它查）
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    # 邮箱：可选
    email: Mapped[str | None] = mapped_column(String(100), nullable=True)
    # 密码哈希：只存密文，永不存明文
    hashed_password: Mapped[str] = mapped_column(String(200))
    # 创建时间：由数据库端生成默认值
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())

# models 数据库映射对象
import datetime

from sqlalchemy import Column, String, func
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped


class Base(DeclarativeBase):
    pass

class User(Base):
    # 表名
    __tablename__ = "users"
    id:Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    name:Mapped[str] = mapped_column(String(100),nullable=True)
    email:Mapped[str] = mapped_column(String(100),nullable=True)
    create_at:Mapped[datetime.datetime] = mapped_column(server_default=func.now())


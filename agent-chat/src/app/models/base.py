# 所有 ORM 模型的公共基类：metadata 集中管理，建表时一次 create_all 全部建
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass

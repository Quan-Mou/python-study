# 数据库访问，mapper,dao
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.users import User

class UserRepository:
    def __init__(self,db:Session):
        self.db=db

    def create_user(self,name,email) -> User:
        user = User(name=name, email=email)
        self.db.add(user)
        self.db.commit()
        # 刷新，拿到插入的user
        self.db.refresh(user)
        return user

    def get_user_by_name(self,name:str) -> User | None:
        # name 不唯一，取第一条；scalar_one_or_none 遇到同名多行会抛 MultipleResultsFound
        return self.db.execute(select(User).where(User.name==name)).scalars().first()

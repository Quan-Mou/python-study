# 业务逻辑层 java中一般需要接口+实现类service
from fastapi import HTTPException

from app.models.users import User
from app.repositories.user_repo import UserRepository
from app.schemas.user import UserResponse


# api->services->repositories->models->schema

class UserService:
    def __init__(self,repo:UserRepository):
        self.repo = repo

    def create_user(self,name:str,email:str) -> UserResponse:
        user  = self.repo.create_user(name=name,email=email)
        # 这一步相当于 Spring中的copyBean
        return UserResponse.model_validate(user)

    def get_user_by_name(self,name:str) -> UserResponse:
        user = self.repo.get_user_by_name(name=name)
        if user is None:
            raise HTTPException(410,"用户不存在")
        # 这一步相当于 Spring中的copyBean
        return UserResponse.model_validate(user)


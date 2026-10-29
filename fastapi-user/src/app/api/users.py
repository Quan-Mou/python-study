# 路由模块，相当于java的controller层
from fastapi import APIRouter, Depends

from app.core.deps import get_db
from app.repositories.user_repo import UserRepository
from app.schemas.user import UserResponse, UserCreate
from app.services.user_services import UserService

router = APIRouter(prefix="/users", tags=["users"])

def get_user_service(db=Depends(get_db)) -> UserService:
    # 这里为什么使用Depends获取get_db的结果，和get_db里的yield的关系？
    return UserService(repo=UserRepository(db))


@router.post("/save",response_model=UserResponse)
def save_user(user: UserCreate, service: UserService = Depends(get_user_service)):
    return service.create_user(name=user.name, email=user.email)

@router.get("/getUser",response_model=UserResponse)
def get_user(user_name:str,service:UserService = Depends(get_user_service)):
    return service.get_user_by_name(user_name)

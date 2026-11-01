import jwt
from fastapi import HTTPException, Depends, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from jwt import InvalidTokenError

from app.core.config import app_settings
from app.core.deps import get_db
from app.core.security import RegisterRequest, hash_password, verify_password, create_access_token
from app.repositories.user_repo import UserRepository

router = APIRouter(tags=["auth"])


# 用户注册
@router.post("/register")
def register(user: RegisterRequest, db=Depends(get_db)):
    user_repo = UserRepository(db=db)
    user_info = user_repo.get_user_by_name(user.username)
    if user_info is not None:
        raise HTTPException(status_code=400, detail="User already exists")

    # 密码哈希后存入 hashed_password 列，明文不落库
    hash_pwd = hash_password(user.password)
    user_repo.create_user(name=user.username, email="", hashed_password=hash_pwd)
    return {
        "status": 200,
        "msg": "User created successfully",
    }


@router.post("/login-user")
def login_user(user: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db)):
    user_repo = UserRepository(db=db)
    user_info = user_repo.get_user_by_name(user.username)
    print(f"user_info: {user_info}")
    print(f"user:{user}")
    # 老数据的 hashed_password 可能为 NULL（加列前注册的、或走 /users/save 建的），这类账号无法验证密码
    if user_info is None or user_info.hashed_password is None:
        raise HTTPException(status_code=400, detail="用户名或者密码错误或者用户不存在")
    if not verify_password(user.password, user_info.hashed_password):
        raise HTTPException(status_code=400, detail="用户名或者密码错误或者用户不存在")

    return {
        "status": 200,
        "msg": "User login successfully",
        "data": create_access_token(user.username),
    }


@router.get("/getUser")
def get_user(token: str, db=Depends(get_db)):
    get_user_err = HTTPException(401, "token无效或已过期")

    try:
        payload = jwt.decode(token, key=app_settings.secret_key, algorithms=app_settings.ALGORITHM)
    except InvalidTokenError:
        raise get_user_err

    user_name = payload.get("sub")
    if user_name is None:
        raise get_user_err

    user_repo = UserRepository(db=db)
    return user_repo.get_user_by_name(user_name)

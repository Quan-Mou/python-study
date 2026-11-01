# 认证与权限控制：
# 安装认证依赖：pwdlib[argon2] pyJWT python-multipart
# 密码哈希工具，创建JWT与验证，处理OAuth2密码表单格式所需的依赖之一
import datetime

import jwt
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from pydantic import BaseModel, Field
from app.core.config import app_settings

# 签名算法 algorithm 这些配置放在config.py中
# ALGORITHM = "HS256"
# token 有效期 30分钟
# ACCESS_TOKEN_EXPIRE_MINUTES = 30
# secret_key = "asdvsdf"

# 初始化密码哈希器
password_hash = PasswordHash.recommended()


oauth2_schema = OAuth2PasswordBearer(tokenUrl="/login")



# 注册请求体Schema

class RegisterRequest(BaseModel):
    username: str = Field(min_length=1, max_length=30)
    password: str = Field(min_length=6, max_length=20)




#  把明文密码哈希成密文
def hash_password(password: str) -> str:
    return password_hash.hash(password)

# 那用户登录时的明文与密文做验证，注意是验证，不是解密，哈希是不可逆的，只能做对比
def verify_password(password:str,hash_password:str) -> bool:
    return password_hash.verify(password,hash_password)


# 创建jwt
def create_access_token(user_name:str) -> str:
    expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
        minutes=app_settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": user_name,
        "exp": expires_at
    }

    return jwt.encode(payload=payload,key=app_settings.secret_key,algorithm=app_settings.ALGORITHM)



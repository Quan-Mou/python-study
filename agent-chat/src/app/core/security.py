# 认证与安全：密码哈希 + JWT 生成/解码
import datetime

import jwt
from pwdlib import PasswordHash

from app.core.config import settings

# 密码哈希器：pwdlib 自动挑选当前推荐算法（Argon2），并内置加盐
password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    # 明文 → 哈希密文。哈希是单向不可逆的，只能"加密后对比"，无法"解密"
    return password_hash.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    # 登录时用明文和库里的哈希做对比校验，返回是否匹配
    return password_hash.verify(password, hashed)


def create_access_token(user_id: int, username: str) -> str:
    # 过期时间 = 当前 UTC 时间 + 配置的有效期（用内置 timezone.utc，无需 tzdata）
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
        minutes=settings.access_token_expire_minutes
    )
    # payload：sub 放用户主键（后续据此查库），username 放用户名，exp 放过期时间
    payload = {"sub": str(user_id), "username": username, "exp": expire}
    # 用密钥和算法签名，生成 JWT 字符串
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> dict:
    # 解码并校验签名 + 过期时间；不合法会抛 jwt 异常，由调用方捕获处理
    return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])

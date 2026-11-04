# 认证依赖：从请求头解析 Bearer token，校验后返回当前登录用户
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User

# HTTPBearer：约定客户端在请求头里带 Authorization: Bearer <token>
# auto_error=False：没有 token 时不立刻报错，交给下面手动处理（便于返回自定义信息）
bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    # 请求头解析出的凭证（可能为 None）
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    # 数据库 session（复用 get_db 依赖）
    db: AsyncSession = Depends(get_db),
) -> User:
    # 没有凭证 → 401
    if credentials is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "未提供认证凭证")

    # 校验签名/过期，失败一律 401（不泄露具体原因）
    try:
        payload = jwt.decode(
            credentials.credentials, settings.secret_key, algorithms=[settings.algorithm]
        )
    except jwt.InvalidTokenError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "token 无效或已过期")

    # payload 里的 sub 就是用户主键
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "token 无效或已过期")

    # 按主键查用户，不存在（比如已被删除）→ 401
    user = await db.get(User, int(user_id))
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "用户不存在")

    return user

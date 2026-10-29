# 数据库配置
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import app_settings

# engine 是连接池，全项目共享一个实例（原来叫 session，容易和会话混淆）
engine = create_engine(url=app_settings.database_url)

SessionLocal = sessionmaker(bind=engine)


# yield 依赖：请求进来时执行到 yield，把 Session 注入路由；请求结束后走 finally 关闭
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

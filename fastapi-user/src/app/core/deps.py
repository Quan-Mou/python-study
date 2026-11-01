# 数据库配置
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import app_settings

# SQLAlchemy 内置日志：echo=True 时，所有生成的 SQL（含参数）都会打到 stdout
# 也可用 logging 控制：sqlalchemy.engine 的 logger 设为 INFO，效果等同但更灵活（能接日志文件/格式化）
# 二者只能开一个，同时开会重复打印两遍

# echo=True：控制台直接打印每条
engine = create_engine(url=app_settings.database_url, echo=True)

SessionLocal = sessionmaker(bind=engine)


# yield 依赖：请求进来时执行到 yield，把 Session 注入路由；请求结束后走 finally 关闭
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

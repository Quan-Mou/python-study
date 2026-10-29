import asyncio
import datetime

import uvicorn
from fastapi import FastAPI, Depends
from sqlalchemy import String, func, select, update
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


app = FastAPI()


DATABASE_URL= "mysql+aiomysql://root:123456@127.0.0.1:3306/python_learn?charset=utf8mb4"

engine = create_async_engine(
    DATABASE_URL,
    echo=True, # 打印日志

)
#  创建会话
async_session = async_sessionmaker(engine,expire_on_commit=False)


# DeclarativeBase 不能直接当模型父类，必须先派生一个自己的 Base
class Base(DeclarativeBase):
    pass


# 只有继承了该类，对象才会被SQLAlchemy识别为表映射
class Users(Base):
    __tablename__ = "users"

    id:Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    name:Mapped[str] = mapped_column(String(100),nullable=False)
    email:Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
    #     类似java的toString方法
    def __repr__(self):
        return f"<Users(id={self.id}, name='{self.name}', email='{self.email}')>"


# 创建表
async def db_init():
    async with engine.begin() as conn:
        # 会扫描所有Base的子类对象，创建对应表
        await conn.run_sync(Base.metadata.create_all)



# CRUD操作：

async def get_db() -> AsyncSession:  # 这个AsyncSession
    with async_session() as session:  # 创建新的数据库会话
        try:
            # 生成器语法，执行到这里，函数暂停，把session交给路由函数使用
            # 路由函数：就是@app.get()，@app.post这些装饰器函数，路由函数执行完毕才会执行下面的代码
            yield session  #
            await session.commit()  # 正常执行完 提交事务
        except Exception:
            await session.rollback()  # 发生异常回滚事务
            raise  # 向上抛出异常
        finally:
            await session.close()  # 关闭会话，数据库连接


# 增
async def create_user(user:Users,db:AsyncSession) -> Users:
    db.add(user)
    await db.flush() # flush 获取自增id，但不提交事务
    await db.refresh(user) # 刷新获取服务端生成的字段
    return user


# 删
async def delete_user(id:int,db:AsyncSession) -> int:
    # 先获取用户是否存在，再执行删除
    user = await get_user_by_id(id,db)
    if not user:
        return -1
    await db.delete(user)
    return 1


# 改
async def update_user(user:Users,db:AsyncSession) -> bool:
    stml  = update(Users).where(Users.id == user.id).values(name=user.name, email=user.email)
    result = await db.execute(stml)

    return result.rowcount > 0

# 查
async def get_users(db:AsyncSession,skip:int = 0,limit:int = 100) -> list[Users]:
    # select * from Users limit skip limit order by id
    result = await db.execute(select(Users).offset(skip).limit(limit).order_by(Users.id))
    #
    return list(result.scalars().all())


# 根据id查询用户
async def get_user_by_id(id:int,db:AsyncSession) -> Users:
    result = await db.execute(select(Users).where(Users.id == id))
    return result.scalar_one_or_none()



async def local_test():
    # 初始化表结构
    await db_init()
    print("表创建完成")
    async with async_session() as db:
        try:
            users = await get_users(db)
            print(f"初始用户数据：{users}")

            # 新增一条数据
            user1 = Users(name="张三",email="2312038309@qq.com")
            new_user = await create_user(user1,db)
            print(f"新增一条用户数据：{new_user}")
            await db.commit()

            # 再次查询
            user2 = await get_users(db)
            print(f"最新用户数据：{user2}")

            print("开始修改用户数据")
            user1.name = "韩立"
            is_update = await update_user(user1,db)
            await db.commit()
            if is_update:
                print(f"修改用户信息成功，最新用户数据")
            else:
                print("用户数据修改失败")

            # 查询所有用户数据
            news_users = await get_users(db)
            print(f"最新的所有用户数据：{news_users}")

            # 新增一条用户数据
            user2 = Users(name="沃伦巴菲特",email="2312@qq.com")
            news_user2 = await create_user(user=user2,db=db)
            print(f"创建用户成功：{news_user2}")
            await db.commit()

            # 删除一条用户信息
            rows = await delete_user(news_user2.id,db)
            if rows > 0:
                print("删除用户成功")
            await  db.commit()
            # 打印所有用户信息
            all_user = await get_users(db)
            print(f"所有用户信息：{all_user}")
        except Exception as e:
            print(f"测试出错:{e}")
        finally:
            await engine.dispose()


if __name__ == "__main__":

    asyncio.run(local_test())













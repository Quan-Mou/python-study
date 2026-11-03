from fastapi import FastAPI
from pydantic import BaseModel

import asyncio

app = FastAPI()



class UserCreate(BaseModel):
    name:str
    age:int



@app.get("/hello")
def hello():
    return {
        "message": "Hello FastAPI"
    }


# async def 定义的路由：运行在事件循环上，I/O 等待时可切换处理其他请求
@app.get("/async")
async def async_hello():
    await asyncio.sleep(0.1)  # 模拟一次异步 I/O（如查库、调外部接口）
    return {
        "message": "Hello Async"
    }


@app.post("/user")
def create_user(user:UserCreate):
    return {
        "name": user.name,
        "age": user.age
    }


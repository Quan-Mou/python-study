"""Lesson 01 —— 最小应用：路由、路径参数、查询参数

运行：
    uv run uvicorn fastapi_learning.demo_hello:app --reload

打开交互式文档（自动生成的 Swagger UI）：
    http://127.0.0.1:8000/docs
"""
from fastapi import FastAPI

# FastAPI 实例：title 会显示在 /docs 页面上
app = FastAPI(title="Lesson 01 - Hello FastAPI")


# 最简单的路由：GET http://127.0.0.1:8000/
@app.get("/")
def root():
    return {"message": "Hello FastAPI"}


# 路径参数：URL 里的 {item_id} 会作为同名函数参数传入。
# 类型注解 int 会被 FastAPI 自动转换 + 校验，
# 传 /items/abc 会直接返回 422 校验错误，不用手写解析代码。
@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}


# 查询参数：没有出现在路径里的函数参数自动变成 ?key=value。
# q: str | None = None → 可选参数；skip/limit 有默认值。
# 访问示例：/search?q=python&skip=0&limit=5
@app.get("/search")
def search(q: str | None = None, skip: int = 0, limit: int = 10):
    return {"q": q, "skip": skip, "limit": limit}


# 直接运行本文件时启动服务器（方便 IDE 一键运行 / python demo_hello.py）
# 等价于命令行：uv run python -m uvicorn fastapi_learning.demo_hello:app --reload
if __name__ == "__main__":
    import uvicorn

    # reload=True 时必须传 import 字符串而不是 app 对象，
    # 否则热重载的子进程找不到应用
    uvicorn.run(
        "fastapi_learning.demo_hello:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )

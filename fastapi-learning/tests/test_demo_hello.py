"""Lesson 00 —— 用 TestClient 测试接口（不需要真正启动服务器）"""
from fastapi.testclient import TestClient

from fastapi_learning.demo_hello import app

client = TestClient(app)


def test_root():
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json() == {"message": "Hello FastAPI"}


def test_path_param_type_checked():
    # 类型注解 int 自动生效
    assert client.get("/items/42").json() == {"item_id": 42}
    # 传非数字 → FastAPI 自动返回 422 校验错误
    assert client.get("/items/abc").status_code == 422


def test_query_params():
    resp = client.get("/search", params={"q": "python", "limit": 5})
    assert resp.json() == {"q": "python", "skip": 0, "limit": 5}

    # 不传参数时全部使用默认值
    assert client.get("/search").json() == {"q": None, "skip": 0, "limit": 10}

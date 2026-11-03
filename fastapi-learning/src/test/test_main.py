from fastapi.testclient import TestClient

from .main import app  # 包内相对导入：参照 test 包自身，不依赖运行时的工作目录

client = TestClient(app)



# FastAPI提供了测试客户端，在启动http服务器的情况下测试接口

def test_hello():
    response = client.get("/hello")

    print(response.json())
    print(response.status_code)
    assert response.status_code == 200

    assert response.json() == {
        "message": "Hello FastAPI"
    }


def test_user():
    response = client.post(
        "/user",
            json={
                "name": "quanmou",
                "age":20
            }
    )

    assert response.status_code == 200

    data = response.json()

    print(data["name"])
    print(data["age"])
    assert data["name"] == "quanmou"
    assert data["age"] == 20




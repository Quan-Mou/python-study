# 认证接口测试：注册 / 登录 / 重复注册 / 错误密码 / 鉴权
async def test_register_success(client):
    resp = await client.post(
        "/api/auth/register", json={"username": "bob", "password": "secret123"}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["username"] == "bob"
    assert "hashed_password" not in body  # 密码哈希绝不返回给前端


async def test_register_duplicate_username(client):
    # 第一次注册成功
    await client.post("/api/auth/register", json={"username": "bob", "password": "secret123"})
    # 同名再注册 → 400
    resp = await client.post("/api/auth/register", json={"username": "bob", "password": "secret123"})
    assert resp.status_code == 400


async def test_login_wrong_password(client):
    await client.post("/api/auth/register", json={"username": "carol", "password": "secret123"})
    # 密码错误 → 400
    resp = await client.post(
        "/api/auth/login", json={"username": "carol", "password": "wrong-pass"}
    )
    assert resp.status_code == 400


async def test_me_requires_token(client):
    # 不带 token 访问受保护接口 → 401
    resp = await client.get("/api/auth/me")
    assert resp.status_code == 401


async def test_me_with_token(client, token):
    # 带 token → 200 并返回当前用户
    resp = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["username"] == "alice"

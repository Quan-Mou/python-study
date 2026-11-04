# 聊天接口测试：SSE 流式 + 历史记录 + 鉴权
async def test_chat_streams_sse(client, token):
    # 带 token 发聊天请求，期望返回 text/event-stream 流
    resp = await client.post(
        "/api/chat",
        json={"content": "你好"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/event-stream")

    # 流式内容应包含 token 事件和 done 事件，且完整回复含假模型的固定答复
    assert '"type": "token"' in resp.text
    assert '"type": "done"' in resp.text
    assert "你好，我是测试助手。" in resp.text


async def test_chat_requires_auth(client):
    # 不带 token → 401
    resp = await client.post("/api/chat", json={"content": "你好"})
    assert resp.status_code == 401


async def test_history_records_messages(client, token):
    # 先发一轮聊天
    resp = await client.post(
        "/api/chat",
        json={"content": "第一次提问"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200

    # 从流式响应里无法直接拿 thread_id，这里通过再建一个已知 thread_id 的会话来验证历史
    resp2 = await client.post(
        "/api/chat",
        json={"content": "续聊", "thread_id": "fixed-thread-1"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp2.status_code == 200

    # 查历史：应返回 2 条（user + assistant）
    hist = await client.get(
        "/api/chat/history/fixed-thread-1",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert hist.status_code == 200
    msgs = hist.json()
    assert len(msgs) == 2
    assert msgs[0]["role"] == "user"
    assert msgs[0]["content"] == "续聊"
    assert msgs[1]["role"] == "assistant"

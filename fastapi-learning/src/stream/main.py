import asyncio
import json

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
# from starlette.middleware.cors import CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware
# from starlette.websockets import WebSocket
from fastapi.websockets import WebSocket, WebSocketDisconnect

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
allow_origins=["*"],  #
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def generate():
    for word in ["FastAPI","是一个","python","Web框架"]:
        yield word + "\n" # 生成一段数据，并保留生成器的执行状态
        await asyncio.sleep(1)

@app.get("/stream")
def stream():
    return StreamingResponse( # 将数据逐步发送给客户端,服务端是流式逐发的，如果浏览器展示不是流式接受，是因为浏览器对text/plain的渲染有缓冲。后面换成 text/event-stream
        generate(),
        media_type="text/plain"
    )



async def event_generate():
    words = [
        "你好",
         "学习",
        "FastAPI",
        "这是一个",
        "SSE 流式接口"
    ]

    for index,word in enumerate(words):
        data = {
            "index": index,
            "content": word,
        }

        # SSE 协议要求每条消息以 data: 开头，ensure_ascii保证中文不会被转成 \uXXX
        # 每次yield都会产生一条SSE消息，StreamingResponse 会从这里取消息并推送给浏览器
        yield f"data:{json.dumps(data,ensure_ascii=False)}\n\n" # 最后一定不要包含空格，空行表示结束的标志，
        # \n 下一行
        # \n\n 空行



        #  模拟一秒的延迟
        await asyncio.sleep(1)

    #  发送一个自定义时间 done，告诉前端流已经结束
    yield "event:done\ndata:{}\n\n"


@app.get("/sse")
def sse():
    return StreamingResponse(
        event_generate(), # 传入异步生成器，FastAPI会不断读取它产生的数据
        media_type="text/event-stream",
        headers={
            "Cache-control":"no-cache", # 禁止缓存，保证前端能实时接受新数据
            "X-Accel-Buffering":"no" # 关闭Nginx等反向代理的缓冲，避免数据被积攒在一起，一次性返回
        }
    )




@app.websocket("/ws")
async def websocket_endpoint(websocket:WebSocket):
    # 接受握手请求，正式建立WebSocket连接
    await websocket.accept()
    try:
        # 死循环，持续监听客户端发送的消息
        while True:
            # 异步阻塞，直到获取到客户端发送的消息
            message = await websocket.receive_text()

            await websocket.send_text(f"获取到客户端发送的消息：{message}")

    except WebSocketDisconnect:
        print("客户端断开连接")



# 连接管理对象
class ConnectionManager:
    def __init__(self):
        # 存放连接的对象
        self.active_connections:dict[int,WebSocket] = {}

    # 当前在线用户 id 列表
    def online_users(self) -> list[int]:
        return list(self.active_connections.keys())

    # 把在线名单广播给所有人（JSON：谁上线/下线后，每个客户端刷新自己的用户列表）
    async def broadcast_online(self):
        payload = json.dumps({"type": "online", "users": self.online_users()},
                             ensure_ascii=False)
        for ws in list(self.active_connections.values()):
            try:
                await ws.send_text(payload)
            except Exception:
                pass  # 单个连接发送失败不影响其他人

    # 建立连接
    async def connect(self,user_id:int,websocket:WebSocket):

        await websocket.accept()
        self.active_connections[user_id] = websocket
        print(self.active_connections)
        await self.broadcast_online()  # 有人上线 → 全员刷新在线列表

    # 断开连接
    def disconnect(self,user_id:int):
        self.active_connections.pop(user_id,None)

    # 断开后广播在线名单（disconnect 是同步方法，由端点在断开后异步调用）
    async def broadcast_after_disconnect(self, user_id:int):
        print(f"用户：{user_id} 断开连接")
        await self.broadcast_online()

    # 发送消息（修复：send_text 是协程，必须 await 才真正发出）
    async def send_msg(self,user_id:int,msg:str):
        websocket = self.active_connections.get(user_id,None)
        if websocket:
            await websocket.send_text(msg)


# 统一的消息封包：前端按 type 字段区分"系统事件"和"聊天消息"
def chat_payload(from_user:int, msg:str) -> str:
    return json.dumps({"type": "chat", "from": from_user, "content": msg},
                      ensure_ascii=False)


manager = ConnectionManager()

@app.websocket("/ws/{user_id}")
async def websocket_endpoint2(
        user_id:int, # FastAPI自动从 路径参数中提取
        websocket:WebSocket # FastAPI自动注入
):
    await manager.connect(user_id, websocket)
    print(f"用户{user_id} 已连接")
    try:
        while True:
            raw = await websocket.receive_text()
            # 协议约定：客户端发 JSON {"to": 目标用户id, "content": 消息}
            # to 为空/为 0 时，行为退回原样：服务端回显给自己
            try:
                data = json.loads(raw)
                to_user = int(data.get("to") or 0)
                content = str(data.get("content", ""))
            except (ValueError, TypeError):
                # 不是 JSON → 按老协议处理，直接回显
                await websocket.send_text(f"收到用户{user_id}发送的消息:{raw}")
                continue

            if to_user and content:
                # 私聊：转发给目标用户，并告知发送方已送达
                await manager.send_msg(to_user, chat_payload(user_id, content))
                await websocket.send_text(chat_payload(user_id, content, ))
                print(f"用户{user_id} -> 用户{to_user}: {content}")
            else:
                await websocket.send_text(f"收到用户{user_id}发送的消息:{content or raw}")

    except WebSocketDisconnect:
        manager.disconnect(user_id)
        print(f"用户：{user_id} 断开连接")
        await manager.broadcast_after_disconnect(user_id)














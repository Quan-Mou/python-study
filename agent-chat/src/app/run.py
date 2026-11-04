# 开发服务器启动入口：uv run dev 等价于 uvicorn app.main:app
import uvicorn


def main() -> None:
    # reload=True 改动自动重载；生产请去掉
    uvicorn.run("app.main:app", host="127.0.0.1", port=8082, reload=True)

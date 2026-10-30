# 提供依赖后的开发服务器启动入口：uv run dev
# 等价于 uvicorn app.main:app --host 127.0.0.1 --port 8081
import uvicorn


def main() -> None:
    uvicorn.run("app.main:app", host="127.0.0.1", port=8081, reload=True)

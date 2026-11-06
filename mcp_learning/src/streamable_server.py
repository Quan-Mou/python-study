from mcp.server import FastMCP


# 通过 Streamable HTTP 对外提供 MCP 服务。
# 默认地址通常是 http://127.0.0.1:8000/mcp。
mcp = FastMCP("company-streamable-server")


@mcp.tool()
def weather(city: str) -> str:
    """根据城市获取天气信息。"""
    return f"{city} 天气永远晴朗"



if __name__ == "__main__":
    # 与 stdio 不同，Streamable HTTP 会启动一个 HTTP 服务。
    # 客户端通过 /mcp 端点连接，而不是通过 stdin/stdout 通信。
    mcp.run(transport="streamable-http")

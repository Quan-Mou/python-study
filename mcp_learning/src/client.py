import asyncio

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
# from langchain.mcp import MCPAdapter
from langchain_mcp_adapters.client import MultiServerMCPClient


# 使用 LangChainClient 连接MCP Server

async def main():

    # 创建MCP Client
    # 这个配置的关键是使用 uv，帮我启动server.py,相当于在客户端内部执行 uv run --directory . python server.py
    #
    #
    client = MultiServerMCPClient(
        {
            "company": { # 自己起的名称
                "transport": "stdio", #langchain-mcp-adapters 的 MultiServerMCPClient 配置
                "command": "uv", # command和args来源于 stdio子进程启动配置
                "args": [
                    "run",
                    "--directory",
                    ".",
                    "python",
                    "server.py"
                ]
            },
            "company-http": {
                "transport": "streamable_http",
                "url": "http://127.0.0.1:8000/mcp",
            }
        }
    )

    # async with MCPAdapter("https://docs.langchain.com/mcp") as adapter:
    #     tools = await adapter.list_tools()


    # 获取工具
    tools = await client.get_tools()
    print("获取到的工具：")
    for tool in tools:
        print(tool.name)
        print(tool.description)

#     创建Agent
    model = init_chat_model(
        model="auto/deepseek-v4-pro",
        model_provider="openai",
        api_key="magpie",
        base_url="http://127.0.0.1:3425/v1"
    )

    agent = create_agent(
        model=model,
        tools=tools,
    )

    result = await agent.ainvoke(
        # {"messages": [{"role": "user", "content": "hi,你是什么模型？"}]},
        {"messages": [{"role": "user", "content": "hi,杭州的天气怎么样？"}]},
    )

    print(result)

if __name__ == "__main__":
    asyncio.run(main())







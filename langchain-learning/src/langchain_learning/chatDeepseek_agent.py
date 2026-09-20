from dotenv import load_dotenv
load_dotenv()

from langchain_deepseek import ChatDeepSeek
from langchain.agents import create_agent

# 1. 初始化 DeepSeek 模型
model = ChatDeepSeek(
    model="deepseek-chat",  # 或 "deepseek-reasoner"
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

def get_weather(city: str) -> str:
    """获取指定城市的天气."""
    return f"{city}的天气一直很好，是25度，晴空万里!"

# 2. 用 ChatDeepSeek 实例创建 Agent
agent = create_agent(
    model=model,  # 直接传入模型实例，而不是字符串
    tools=[get_weather],
    system_prompt="You are a helpful assistant",
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "北京的天气怎么样?"}]}
)
print(result["messages"][-1].content_blocks)
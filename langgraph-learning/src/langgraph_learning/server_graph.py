"""
LangGraph API Server 入口 — 供 langgraph dev 使用

启动方式: uv run langgraph dev
Web 控制台: http://localhost:1420/
"""

import os
from typing import TypedDict

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langgraph.graph import END, START, StateGraph

load_dotenv(override=True)

# ============================================================
# 模型初始化
# ============================================================
api_key = os.getenv("COMPANY_API_KEY")
base_url = os.getenv("COMPANY_BASE_URL")

model = init_chat_model(
    model="qwen3.7-plus",
    model_provider="openai",
    api_key=api_key,
    base_url=base_url,
)


# ============================================================
# 状态声明
# ============================================================
class OverAllState(TypedDict):
    topic: str
    poem: str
    joke: str
    final_output: str


class InputState(TypedDict):
    topic: str


class OutputState(TypedDict):
    final_output: str


# ============================================================
# 节点定义
# ============================================================
def node_change_topic(state: InputState) -> dict:
    return {"topic": f"{state['topic']}:布偶猫"}


def node_poem(state: OverAllState) -> dict:
    poem = model.invoke(
        [HumanMessage(f"写一首关于{state['topic']}主题的七言绝句")]
    ).content
    return {"poem": poem}


def node_joke(state: OverAllState) -> dict:
    joke = model.invoke(
        [HumanMessage(f"写一个关于{state['topic']}主题的笑话")]
    ).content
    return {"joke": joke}


def node_output(state: OverAllState) -> dict:
    return {
        "final_output": f"诗:\n{state['poem']}\n\n笑话:\n{state['joke']}"
    }


# ============================================================
# 构建图
# ============================================================
builder = StateGraph(
    state_schema=OverAllState,
    input_schema=InputState,
    output_schema=OutputState,
)
builder.add_node("node_change_topic", node_change_topic)
builder.add_node("node_poem", node_poem)
builder.add_node("node_joke", node_joke)
builder.add_node("node_output", node_output)

builder.add_edge(START, "node_change_topic")
builder.add_edge("node_change_topic", "node_poem")
builder.add_edge("node_change_topic", "node_joke")
builder.add_edge("node_poem", "node_output")
builder.add_edge("node_joke", "node_output")
builder.add_edge("node_output", END)

# 不传 checkpointer → LangGraph Server 会自动注入
graph = builder.compile()
from typing import Literal
import os
from langchain.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, MessagesState
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv


load_dotenv(override=True)

api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("COMPANY_BASE_URL")

print(api_key)
print(base_url)


@tool
def search(query: str):
    """Call to surf the web."""
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."

tools = [search]
tool_node = ToolNode(tools)


model = init_chat_model(
    model="qwen3.7-plus",
    model_provider="openai",
    api_key=api_key,
    base_url=base_url,
).bind_tools(tools)

# model = ChatOpenAI(model="gpt-6-luna").bind_tools(tools)

# model


def should_continue(state: MessagesState) -> Literal["tools", "__end__"]:
    messages = state['messages']
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return "__end__"

def call_model(state: MessagesState):
    messages = state['messages']
    # Invoking `model` will automatically infer the correct tracing context
    response = model.invoke(messages)
    return {"messages": [response]}

workflow = StateGraph(MessagesState)
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)
workflow.add_edge("__start__", "agent")
workflow.add_conditional_edges(
    "agent",
    should_continue,
)
workflow.add_edge("tools", 'agent')

app = workflow.compile()

# final_state = app.invoke(
#     {"messages": [HumanMessage(content="what is the weather in sf")]},
#     config={"configurable": {"thread_id": 42}}
# )

final_state = app.invoke(
    {"messages": [HumanMessage(content="你好")]},
    config={"configurable": {"thread_id": 42}}
)

final_state["messages"][-1].content
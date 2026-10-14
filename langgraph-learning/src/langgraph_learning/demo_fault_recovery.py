"""
LangGraph 失败恢复（Fault Tolerance）演示

流程图:
    START → node_change_topic → (node_poem, node_joke)  ← 同一个超步（superstep）
                                     ↓
                                node_output → END

关键概念：
  - 同一超步中的节点（node_poem 和 node_joke）并行执行
  - 任一个失败 → 整个超步回滚，checkpoint 回到超步开始前
  - 修复代码后用 invoke(None, config) 从中断点恢复
  - 恢复时，同一超步的两个节点都会重新执行

观察方法：
  运行脚本后，看 get_state_history 输出中是否有相邻两帧的 next 都指向
  ('node_poem', 'node_joke') —— 那就是恢复的证据。
"""

import os
import time
from typing import TypedDict

import rich
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import END, START, StateGraph
from loguru import logger
from rich import print as rprint

load_dotenv(override=True)

# ============================================================
# 初始化模型
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
# 控制失败恢复的全局开关
#   True  → node_joke 会抛异常（模拟 bug）
#   False → node_joke 正常执行（模拟修复后）
# ============================================================
_SIMULATE_FAILURE = True


# ============================================================
# 节点定义
# ============================================================
def node_change_topic(state: InputState) -> OverAllState:
    logger.info("[node_change_topic] 执行中，添加子主题")
    return {"topic": f"{state['topic']}:布偶猫"}


def node_poem(state: OverAllState) -> OverAllState:
    logger.info("[node_poem] 正在生成诗歌...")
    topic = state["topic"]
    poem = model.invoke(
        [HumanMessage(f"写一首关于{topic}主题的七言绝句")]
    ).content
    return {"poem": poem}


def node_joke(state: OverAllState) -> OverAllState:
    logger.info("[node_joke] 正在生成笑话...")

    if _SIMULATE_FAILURE:
        logger.error("[node_joke] 模拟失败！抛出异常！")
        raise RuntimeError("node_joke 人为抛出的异常 —— 模拟线上 bug")

    topic = state["topic"]
    time.sleep(2)
    joke = model.invoke(
        [HumanMessage(f"写一个关于{topic}主题的笑话")]
    ).content
    return {"joke": joke}


def node_output(state: OverAllState) -> OutputState:
    logger.info("[node_output] 正在组装最终输出...")
    final_output = (
        f"关于{state['topic']}的七言绝句:\n{state['poem']}\n\n"
        f"笑话:\n{state['joke']}\n"
    )
    return {"final_output": final_output}


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


# ============================================================
# 主流程
# ============================================================
DB_URL = "postgresql://zqh123123123:123456@localhost:5432/langgraph_db?sslmode=disable"

with PostgresSaver.from_conn_string(DB_URL) as checkpointer:
    checkpointer.setup()
    graph = builder.compile(checkpointer=checkpointer)

    config = {"configurable": {"thread_id": "chapter03-fault-recovery-demo"}}

    rich.print(list(graph.get_state_history(config)))
    # # ── 第一次调用：模拟失败 ──
    # print("\n" + "=" * 60)
    # print("  第 1 次调用：模拟 node_joke 失败")
    # print("=" * 60)
    # try:
    #     result = graph.invoke({"topic": "猫"}, config=config)
    #     rprint("[green]成功:[/green]", result)
    # except Exception as e:
    #     logger.warning(f"第一次调用失败（预期之中）: {e}")
    #
    # # ── 修复 bug：关闭失败开关 ──
    # _SIMULATE_FAILURE = False  # ← 模拟"上线修复"
    # print("\n" + "=" * 60)
    # print("  第 2 次调用：修复后，invoke(None) 从中断点恢复")
    # print("=" * 60)
    #
    # # ── 第二次调用：从中断点恢复 ──
    # result = graph.invoke(None, config=config)
    # rprint("[green]恢复后成功输出:[/green]")
    # rprint(result)
    #
    # # ── 查看 state history ──
    # print("\n" + "=" * 60)
    # print("  State History 分析")
    # print("=" * 60)
    # print("规则: 如果出现相邻两帧的 next 都是 ('node_poem', 'node_joke')")
    # print("      → 说明同一个超步被重新执行了 = 恢复成功 ✅\n")
    #
    # prev_next = None
    # recovery_found = False
    # for i, snap in enumerate(graph.get_state_history(config)):
    #     print(f"--- 第 {i} 帧 ---")
    #     print(f"  next  = {snap.next}")
    #     print(f"  topic = {snap.values.get('topic', '<无>')}")
    #     print(f"  poem  = {'存在' if snap.values.get('poem') else '空'}")
    #     print(f"  joke  = {'存在' if snap.values.get('joke') else '空'}")
    #     print(f"  created_at = {snap.created_at}")
    #     print()
    #
    #     # 检测恢复特征
    #     if (
    #         prev_next == ("node_poem", "node_joke")
    #         and snap.next == ("node_poem", "node_joke")
    #     ):
    #         recovery_found = True
    #         print("  >>> 🔍 发现恢复证据！相邻两帧 next 都指向同一个节点对\n")
    #
    #     prev_next = snap.next if snap.next else None
    #
    # if recovery_found:
    #     print("✅ 成功观察到失败恢复模式！")
    # else:
    #     print("❌ 未观察到恢复模式，请检查脚本执行顺序")
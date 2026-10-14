"""
LangGraph Time Travel 示例：重放（Replay）与 Fork（分支）

重放（Replay）：
    从历史 checkpoint 取出状态，重新 invoke(graph_input, config)，
    让图从那个历史点再次执行。

Fork（分支）：
    从历史 checkpoint 取出 checkpoint_id，用 update_state() 修改
    状态值（相当于"改写历史"），然后用 invoke(None) 继续执行，
    产生一条与原始轨迹不同的分支结果。
"""

import os
from typing import TypedDict

from IPython import display
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import END, START, StateGraph
from loguru import logger
from rich import print as rprint

load_dotenv(override=True)

# ============================================================
# 初始化
# ============================================================
api_key = os.getenv("COMPANY_API_KEY")
base_url = os.getenv("COMPANY_BASE_URL")

model = init_chat_model(
    model="qwen3.7-plus",
    model_provider="openai",
    api_key=api_key,
    base_url=base_url,
)


class OverAllState(TypedDict):
    topic: str
    poem: str
    joke: str
    final_output: str


class InputState(TypedDict):
    topic: str


class OutputState(TypedDict):
    final_output: str


def node_change_topic(state: InputState) -> OverAllState:
    logger.info("[node_change_topic] topic: {}", state["topic"])
    return {"topic": f"{state['topic']}:布偶猫"}


def node_poem(state: OverAllState) -> OverAllState:
    logger.info("[node_poem] 生成诗中...")
    poem = model.invoke(
        [HumanMessage(f"用一句话写关于{state['topic']}的诗")]
    ).content
    return {"poem": poem}


def node_joke(state: OverAllState) -> OverAllState:
    logger.info("[node_joke] 生成笑话中...")
    joke = model.invoke(
        [HumanMessage(f"用一句话写关于{state['topic']}的笑话")]
    ).content
    return {"joke": joke}


def node_output(state: OverAllState) -> OutputState:
    logger.info("[node_output] 组装最终输出...")
    return {
        "final_output": f"诗: {state['poem']}\n笑话: {state['joke']}"
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


# ============================================================
# 主流程
# ============================================================
DB_URL = "postgresql://zqh123123123:123456@localhost:5432/langgraph_db?sslmode=disable"

with PostgresSaver.from_conn_string(DB_URL) as checkpointer:
    checkpointer.setup()
    graph = builder.compile(checkpointer=checkpointer)

    display(graph)

    config = {"configurable": {"thread_id": "chapter03-time-travel"}}

    # ── 首次执行：建立 checkpoint 历史 ──
    print("=" * 60)
    print("  初始执行：topic=猫")
    print("=" * 60)
    graph.invoke({"topic": "猫"}, config=config)

    # ── 获取所有历史快照 ──
    history = list(graph.get_state_history(config))
    print(f"\n共有 {len(history)} 个历史快照\n")

    # ──────────────────────────────────────────────────────
    # 1. 重放（Replay）
    #    从历史 checkpoint 取出状态，重新 invoke，从头再跑一遍
    # ──────────────────────────────────────────────────────
    print("=" * 60)
    print("  重放（Replay）")
    print("  从历史帧取值 → invoke(state, config)")
    print("=" * 60)

    # 拿到"原始 topic=猫"的那一帧（在 change_topic 之前）
    replay_source = None
    for snap in history:
        if snap.values.get("topic") == "猫" and snap.next == ("node_change_topic",):
            replay_source = snap
            break

    if replay_source:
        print(f"重放起点: topic={replay_source.values['topic']}, next={replay_source.next}")
        print("→ 从该 checkpoint 重新执行...\n")
        result = graph.invoke(
            {"topic": replay_source.values["topic"]},
            config=config,
        )
        rprint("[green]重放结果:[/green]")
        rprint(result["final_output"][:200] + "...")

    # ──────────────────────────────────────────────────────
    # 2. Fork（分支）
    #    从历史 checkpoint 取 checkpoint_id，
    #    用 update_state 修改某个字段，然后继续执行
    # ──────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("  Fork（分支）")
    print("  获取历史 checkpoint_id → update_state 改写 → invoke(None)")
    print("=" * 60)

    # 找到"刚执行完 change_topic、还没执行 poem/joke"的那一帧
    fork_source = None
    for snap in history:
        if snap.next == ("node_poem", "node_joke") and snap.values.get("topic"):
            fork_source = snap
            break  # 取最新的那一帧

    if fork_source and fork_source.config["configurable"].get("checkpoint_id"):
        ckpt_id = fork_source.config["configurable"]["checkpoint_id"]

        print(f"Fork 起点 checkpoint_id: {ckpt_id}")
        print(f"当前 topic: {fork_source.values['topic']}")
        print("→ update_state: 把 topic 改为 '猫:金渐层（开分支）'...\n")

        # 直接改状态，绕过 node_change_topic
        graph.update_state(
            config,
            {"topic": "猫:金渐层（开分支）"},
            checkpoint_id=ckpt_id,  # ← 指定从哪个 checkpoint 改
        )

        # 从改写后的状态继续执行
        result = graph.invoke(None, config=config)
        rprint("[green]Fork 分支结果:[/green]")
        rprint(result["final_output"][:200] + "...")

    # ──────────── 最终历史一览 ────────────
    print("\n" + "=" * 60)
    print("  最终 State History 一览")
    print("=" * 60)
    for i, snap in enumerate(graph.get_state_history(config)):
        t = snap.values.get("topic", "<空>")
        n = snap.next
        print(f"帧{i:2d} | topic={t[:30]:30s} | next={str(n):30s} | {snap.created_at}")
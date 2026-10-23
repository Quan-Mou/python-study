import json
import os
from typing import TypedDict

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.config import get_stream_writer
from langgraph.types import interrupt, Command


load_dotenv(override=True)


"""
    报销审核工作流：申请分析，预算查询，生成审核建议，人工审核，执行结果。

"""


# ============================================================
# 1. 初始化 LLM
# ============================================================
# model="glm-5.3-flash",
#     model_provider="openai",

model = init_chat_model(
    model="qwen3.7-plus",
    model_provider="openai",
    api_key=os.getenv("COMPANY_API_KEY"),
    base_url=os.getenv("COMPANY_BASE_URL"),
)

# model = ChatOpenAI(
#     model="openai",
#     api_key=os.getenv("OPENAI_API_KEY"),
#     base_url=os.getenv("OPENAI_BASE_URL"),
#     temperature=0,
# )


# ============================================================
# 2. 定义 State
# ============================================================

class ExpenseState(TypedDict):
    applicant: str
    department: str
    amount: float
    reason: str

    analysis: str
    budget: dict
    review: str

    approved: bool | None
    comment: str
    result: str


# ============================================================
# 3. Node 1：理解报销申请
# ============================================================

def understand_expense(state: ExpenseState):
    writer = get_stream_writer()

    writer({
        "stage": "understand_expense",
        "message": "正在分析报销申请",
        "progress": 10,
    })

    response = model.invoke([
        SystemMessage(
            content=(
                "你是企业报销申请分析助手。"
                "请根据申请人、部门、金额和事由，"
                "用简洁中文概括这笔申请。"
                "这里只做分析，不要直接批准或拒绝。"
            )
        ),
        HumanMessage(
            content=(
                f"申请人：{state['applicant']}\n"
                f"部门：{state['department']}\n"
                f"金额：{state['amount']} 元\n"
                f"事由：{state['reason']}"
            )
        ),
    ])

    analysis = str(response.content)

    writer({
        "stage": "understand_expense",
        "message": "申请分析完成",
        "progress": 25,
    })

    return {"analysis": analysis}


# ============================================================
# 4. Node 2：查询预算工具
# ============================================================

def query_budget_tool(department: str, amount: float) -> dict:
    """
    模拟预算查询工具。
    真实项目中，可以在这里调用数据库或企业内部 API。
    """

    department_budgets = {
        "技术部": 10000.0,
        "市场部": 8000.0,
        "人事部": 5000.0,
    }

    remaining = department_budgets.get(department, 0.0)

    return {
        "department": department,
        "remaining_budget": remaining,
        "requested_amount": amount,
        "within_budget": amount <= remaining,
    }


def query_budget(state: ExpenseState):
    writer = get_stream_writer()

    writer({
        "stage": "query_budget",
        "message": "正在查询部门预算",
        "progress": 35,
    })

    budget = query_budget_tool(
        department=state["department"],
        amount=state["amount"],
    )

    writer({
        "stage": "query_budget",
        "message": "预算查询完成",
        "progress": 45,
    })

    return {"budget": budget}


# ============================================================
# 5. Node 3：LLM 生成审核建议
# ============================================================

def generate_review(state: ExpenseState):
    writer = get_stream_writer()

    writer({
        "stage": "generate_review",
        "message": "正在生成审核建议",
        "progress": 55,
    })

    response = model.invoke([
        SystemMessage(
            content=(
                "你是企业报销审核助手。"
                "根据申请分析和预算信息，生成一段简洁的审核建议。"
                "明确说明金额、预算是否充足和需要人工核实的事项。"
                "你只能提出建议，不能代替人工审批。"
            )
        ),
        HumanMessage(
            content=(
                f"申请分析：{state['analysis']}\n"
                f"预算信息：{json.dumps(state['budget'], ensure_ascii=False)}"
            )
        ),
    ])

    review = str(response.content)

    writer({
        "stage": "generate_review",
        "message": "审核建议生成完成",
        "progress": 70,
    })

    return {"review": review}


# ============================================================
# 6. Node 4：人工审批
# ============================================================

def human_approval(state: ExpenseState):
    writer = get_stream_writer()

    # 注意：恢复时，当前节点会从开头重新执行。
    # 因此这里的进度事件可能再次出现。
    writer({
        "stage": "human_approval",
        "message": "等待人工审批",
        "progress": 80,
    })

    decision = interrupt({
        "type": "expense_approval",
        "message": "请审核这笔报销申请",
        "applicant": state["applicant"],
        "department": state["department"],
        "amount": state["amount"],
        "reason": state["reason"],
        "analysis": state["analysis"],
        "budget": state["budget"],
        "review": state["review"],
        "required_response": {
            "approved": "boolean",
            "comment": "string",
        },
    })

    # 恢复值由调用方传入，节点负责将其映射到 State。
    if not isinstance(decision, dict):
        raise ValueError("审批结果必须是一个字典")

    if not isinstance(decision.get("approved"), bool):
        raise ValueError("approved 必须是布尔值")

    comment = decision.get("comment", "")

    if not isinstance(comment, str):
        raise ValueError("comment 必须是字符串")

    writer({
        "stage": "human_approval",
        "message": "已收到审批结果",
        "progress": 90,
    })

    return {
        "approved": decision["approved"],
        "comment": comment,
    }


# ============================================================
# 7. Node 5：执行审批结果
# ============================================================

def execute_result(state: ExpenseState):
    writer = get_stream_writer()

    if state["approved"]:
        # 模拟登记，不会真正写入财务系统。
        result = (
            f"报销申请已批准。"
            f"申请人：{state['applicant']}，"
            f"金额：{state['amount']} 元，"
            f"审批意见：{state['comment']}"
        )

        writer({
            "stage": "execute_result",
            "message": "报销登记完成（模拟）",
            "progress": 100,
        })

    else:
        result = (
            f"报销申请已拒绝。"
            f"申请人：{state['applicant']}，"
            f"金额：{state['amount']} 元，"
            f"审批意见：{state['comment']}"
        )

        writer({
            "stage": "execute_result",
            "message": "已记录拒绝结果（模拟）",
            "progress": 100,
        })

    return {"result": result}


# ============================================================
# 8. 构建五节点工作流
# ============================================================

builder = StateGraph(ExpenseState)

builder.add_node("understand_expense", understand_expense)
builder.add_node("query_budget", query_budget)
builder.add_node("generate_review", generate_review)
builder.add_node("human_approval", human_approval)
builder.add_node("execute_result", execute_result)

builder.add_edge(START, "understand_expense")
builder.add_edge("understand_expense", "query_budget")
builder.add_edge("query_budget", "generate_review")
builder.add_edge("generate_review", "human_approval")
builder.add_edge("human_approval", "execute_result")
builder.add_edge("execute_result", END)

checkpointer = InMemorySaver()

graph = builder.compile(checkpointer=checkpointer)


# ============================================================
# 9. 统一处理三种流式事件
# ============================================================

def run_stream(inputs):
    """
    同时监听 messages、updates、custom。
    返回本轮是否中断，以及本轮最终 State（若正常结束）。
    """

    interrupted = False
    final_state = None

    for part in graph.stream(
        inputs,
        config=config,
        stream_mode=["messages", "updates", "custom"],
        version="v2",
    ):
        event_type = part["type"]
        data = part["data"]

        if event_type == "messages":
            message_chunk, metadata = data

            # 只显示来自两个 LLM 节点的输出。
            node_name = metadata.get("langgraph_node")

            if (
                node_name in {
                    "understand_expense",
                    "generate_review",
                }
                and message_chunk.content
            ):
                content = message_chunk.content

                if isinstance(content, str):
                    print(
                        f"\n[LLM Token | {node_name}] "
                        f"{content}",
                        end="",
                        flush=True,
                    )

        elif event_type == "custom":
            print(
                "\n[CUSTOM 业务进度] "
                + json.dumps(data, ensure_ascii=False)
            )

        elif event_type == "updates":
            print(f"\n[UPDATES 节点更新] {json.dumps(data, ensure_ascii=False, default=str)}")

            # 正确识别 LangGraph 的中断事件
            if "__interrupt__" in data:
                interrupted = True
                print("\n检测到人工审批中断，等待用户输入...")
            # print(
            #     "\n[UPDATES 节点更新] "
            #     + json.dumps(data, ensure_ascii=False, default=str)
            # )
            #
            # # v2 流模式下，中断信息会随对应更新事件暴露。
            # for node_update in data.values():
            #     if isinstance(node_update, dict):
            #         if "__interrupt__" in node_update:
            #             interrupted = True

        elif event_type == "values":
            # 本例没有订阅 values，保留分支便于扩展。
            final_state = data

    if not interrupted:
        # 从 Checkpointer 读取最终状态，便于展示结果。
        snapshot = graph.get_state(config)

        if snapshot and not snapshot.next:
            final_state = snapshot.values

    return interrupted, final_state


# ============================================================
# 10. 启动工作流，并在终端中完成审批
# ============================================================

if __name__ == "__main__":
    config = {
        "configurable": {
            "thread_id": "expense-demo-001"
        }
    }

    initial_state: ExpenseState = {
        "applicant": "张三",
        "department": "技术部",
        "amount": 1200.0,
        "reason": "购买开发测试设备",

        "analysis": "",
        "budget": {},
        "review": "",

        "approved": None,
        "comment": "",
        "result": "",
    }

    print("=" * 60)
    print("第一阶段：执行报销审核工作流")
    print("=" * 60)

    interrupted, final_state = run_stream(initial_state)

    if interrupted:
        print("\n\n工作流已暂停，等待人工审批。")

        # 从保存的状态中读取中断信息。
        snapshot = graph.get_state(config)

        for task in snapshot.tasks:
            for intr in task.interrupts:
                print("\n待审批信息：")
                print(json.dumps(
                    intr.value,
                    ensure_ascii=False,
                    indent=2,
                    default=str,
                ))

        decision_text = input(
            "\n请输入审批结果（y=批准，n=拒绝）："
        ).strip().lower()

        if decision_text not in {"y", "n"}:
            print("输入无效。当前工作流仍处于等待审批状态。")
            raise SystemExit(1)

        comment = input("请输入审批意见：").strip()

        resume_value = {
            "approved": decision_text == "y",
            "comment": comment,
        }

        print("\n" + "=" * 60)
        print("第二阶段：恢复工作流")
        print("=" * 60)

        interrupted, final_state = run_stream(
            Command(resume=resume_value)
        )

    if interrupted:
        print("\n工作流仍处于中断状态。")
    elif final_state:
        print("\n" + "=" * 60)
        print("最终执行结果")
        print("=" * 60)
        print(final_state.get("result"))
    else:
        print("未能读取最终状态，请检查执行日志。")
"""
main.py —— 命令行交互入口
==========================

整体流程（LangChain Agent 的经典工作模式）：

    用户输入
       ↓
    大模型思考 → 决定调用哪个工具（tool_calls）
       ↓
    LangChain 框架自动执行工具函数，把结果塞回对话（ToolMessage）
       ↓
    大模型看到工具结果 → 继续思考：还需要别的工具？还是可以回答了？
       ↓（循环）
    生成最终回答（AIMessage）

这个"思考 → 调用工具 → 观察结果 → 再思考"的循环就是 Agent（智能体）的本质，
而循环的调度由 create_agent 创建的 LangGraph 自动完成，我们只需要提供模型和工具。

运行方式：在 smart-assistant 目录下执行
    uv run smart-assistant
"""

from langchain.agents import create_agent
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text

from smart_assistant.config import get_llm
from smart_assistant.tools import ALL_TOOLS

console = Console()

print(ALL_TOOLS[0])

# 系统提示词：给智能体设定"人设"和行为规则，每次对话都会放在消息列表最前面
SYSTEM_PROMPT = (
    "你是一个多功能智能助手，帮助用户解答问题。"
    "你可以使用这些工具：天气查询、数学计算、时间查询、货币转换、信息搜索。"
    "规则：1. 涉及计算时必须调用 calculate 工具，不要自己心算；"
    "2. 用户问天气、时间、汇率、搜索类问题时，优先调用对应工具获取数据再回答；"
    "3. 闲聊或不涉及工具的问题直接回答；4. 始终使用中文回答。"
)


def _to_text(content) -> str:
    """把消息 content 统一转成字符串（有些模型返回字符串，有些返回分段列表）。"""
    if isinstance(content, str):
        return content
    if isinstance(content, list):  # 内容分块列表 → 拼接其中的文本块
        return "".join(
            part.get("text", "") if isinstance(part, dict) else str(part)
            for part in content
        )
    return str(content) if content else ""


def _print_message(msg) -> None:
    """
    把一条消息渲染成带颜色的面板，让"Agent 的思考过程"可视化：

    - HumanMessage（用户输入）→ 跳过（输入时已经打印过了）
    - AIMessage 且带 tool_calls → 黄色面板：模型决定调用什么工具
    - ToolMessage（工具执行结果）→ 青色面板：工具返回了什么
    - AIMessage 最终回答 → 绿色面板 + Markdown 渲染
    """
    if isinstance(msg, HumanMessage):
        return

    if isinstance(msg, AIMessage) and msg.tool_calls:
        # 模型"决定调用工具"的消息，tool_calls 里存着工具名和参数
        for call in msg.tool_calls:
            console.print(
                Panel(
                    f"工具: {call['name']}    参数: {call['args']}",
                    title="🔧 智能体调用工具",
                    border_style="yellow",
                )
            )
        # 有些模型调用工具的同时还会输出一段说明文字，有就一并显示
        text = _to_text(msg.content)
        if text.strip():
            console.print(f"[dim]（模型说明）{text}[/dim]\n")
        return

    if isinstance(msg, ToolMessage):
        console.print(
            Panel(
                _to_text(msg.content),
                title=f"📋 工具 {msg.name} 返回结果",
                border_style="cyan",
            )
        )
        return

    if isinstance(msg, AIMessage):
        text = _to_text(msg.content)
        if text.strip():  # 最终回答用 Markdown 渲染，更好看
            console.print(
                Panel(Markdown(text), title="🤖 智能助手", border_style="green")
            )


def main() -> None:
    """启动命令行交互循环。"""

    # ===== 1. 创建 Agent：模型 + 工具 + 系统提示词，三件套 =====
    # create_agent 返回一个 LangGraph 编译好的图（graph），
    # 它内部实现了"模型↔工具"的自动循环调度
    agent = create_agent(
        model=get_llm(),       # 聊天模型（见 config.py）
        tools=ALL_TOOLS,       # 工具列表（见 tools.py）
        system_prompt=SYSTEM_PROMPT,
    )

    # ===== 2. 欢迎信息 =====
    tool_names = "、".join(t.name for t in ALL_TOOLS)
    console.print(
        Panel(
            Text(
                "我是多功能智能助手，可以帮你：\n"
                "  🌤️  天气查询    🧮 数学计算\n"
                "  🕐 时间查询    💱 货币转换\n"
                "  🔍 信息搜索\n\n"
                f"已注册工具：{tool_names}\n"
                "输入 q / quit / exit / 退出 结束对话",
                justify="left",
            ),
            title="✨ 多功能智能助手（LangChain Agent 学习版）",
            border_style="magenta",
        )
    )

    # ===== 3. 交互循环 =====
    while True:
        try:
            user_input = console.input("\n[bold cyan]你 > [/bold cyan]").strip()
        except (KeyboardInterrupt, EOFError):  # Ctrl+C / Ctrl+Z 优雅退出
            console.print("\n[yellow]再见！[/yellow]")
            break

        if not user_input:
            continue
        if user_input.lower() in {"q", "quit", "exit", "退出"}:
            console.print("[yellow]再见！[/yellow]")
            break

        # ===== 4. 调用 Agent 并实时打印过程 =====
        # stream(stream_mode="values")：每走一步图节点，就把【完整消息列表】吐出来一次。
        # 我们每次只看最后一条新消息，就能实时看到：
        #   模型决定调工具 → 工具返回 → 模型再决定 → …… → 最终回答
        # 消息列表会不断增长，历史全部保留，因此助手能理解上下文（多轮对话）。
        try:
            for state in agent.stream(
                {"messages": [HumanMessage(content=user_input)]},
                stream_mode="values",
            ):
                _print_message(state["messages"][-1])
        except Exception as e:
            console.print(f"[red]出错了：{e}[/red]")


if __name__ == "__main__":
    main()

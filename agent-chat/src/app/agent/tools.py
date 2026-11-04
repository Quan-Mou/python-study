# Agent 可调用的工具：纯 Python 实现，无需额外 API key，开箱即用
import datetime

from langchain_core.tools import tool

# 东八区（北京时间）：中国无夏令时，用固定 +8 偏移即可，不依赖 tzdata
_CN_TZ = datetime.timezone(datetime.timedelta(hours=8))


@tool
def get_current_time() -> str:
    """获取当前日期和时间。当用户询问"现在几点""今天几号"等时间问题时调用。"""
    now = datetime.datetime.now(_CN_TZ)
    return now.strftime("%Y-%m-%d %H:%M:%S")


@tool
def calculator(expression: str) -> str:
    """计算一个四则运算表达式，例如 '3*4+2'。当用户要求做数学计算时调用。"""
    try:
        # 用受限命名空间求值，屏蔽内建函数（学习用；生产请换成安全解析器，eval 有注入风险）
        result = eval(expression, {"__builtins__": {}}, {})
        return f"{expression} = {result}"
    except Exception as e:  # noqa: BLE001 表达式非法时返回错误信息而非崩溃
        return f"计算失败：{e}"


# 工具清单：create_react_agent 会把这些工具绑定给模型
TOOLS = [get_current_time, calculator]

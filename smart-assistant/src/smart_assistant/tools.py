"""
tools.py —— 工具集（本项目的核心学习文件）
==========================================

学习要点：
1. @tool 装饰器：把一个普通 Python 函数变成 LangChain 能识别的"工具"（Tool 对象）。
   LangChain 会自动从函数签名中提取：函数名、参数名、参数类型、docstring。

2. docstring 就是"工具说明书"：
   大模型并不会真正执行你的代码，它只读 docstring + 参数注解来决定
   "什么问题该调用哪个工具、参数怎么填"。
   所以 docstring 必须写清楚：① 这个工具能干什么 ② 什么时候该用它 ③ 每个参数的含义。
   （第一行是功能概述，后面补充详细说明，Args 部分描述参数。）

3. 类型注解（str / float 等）会转换成 JSON Schema 传给大模型，
   注解写错会导致模型传错类型的参数。

4. 工具函数的返回值：LangChain 会自动 str() 转成字符串塞进对话（ToolMessage），
   所以直接返回格式化好的中文文本即可。

5. 本文件所有工具都是【模拟实现】（返回假数据），目的是学习工具机制本身。
   真实项目里只需把函数体替换成真正的 API 调用（天气 API、汇率 API、搜索引擎等），
   Agent 的其余代码一行都不用改 —— 这就是"工具抽象"的好处。
"""

import ast
import operator
import random
from datetime import datetime
from zoneinfo import ZoneInfo  # Python 3.9+ 内置时区库，无需安装第三方包
# 注意：Windows 系统没有自带 IANA 时区数据库，需要额外安装 tzdata 包（已在 pyproject.toml 声明）

from langchain.tools import tool


# ======================================================================
# 工具 1：天气查询（模拟）
# ======================================================================
@tool
def get_weather(city: str) -> str:
    """查询指定城市今天的天气情况。

    当用户询问某个城市的天气、气温、是否下雨等问题时，使用此工具。

    Args:
        city: 城市名称，例如 "北京"、"上海"、"广州"
    """
    # --- 模拟数据：预设几个城市的天气，其他城市随机生成 ---
    fake_weather_db = {
        "北京": ("晴", 11, 23, "西北风 3 级", 32),
        "上海": ("多云", 18, 26, "东风 2 级", 65),
        "广州": ("阵雨", 24, 31, "南风 2 级", 85),
        "深圳": ("多云转晴", 25, 30, "微风", 70),
        "杭州": ("晴转多云", 19, 28, "东南风 2 级", 60),
        "成都": ("阴", 17, 22, "无持续风向", 78),
    }
    if city in fake_weather_db:
        condition, low, high, wind, humidity = fake_weather_db[city]
    else:
        # 数据库里没有的城市 → 随机编一条（模拟数据，仅用于演示）
        condition = random.choice(["晴", "多云", "阴", "小雨"])
        low, high = random.randint(5, 20), random.randint(21, 33)
        wind = random.choice(["微风", "东风 2 级", "南风 3 级"])
        humidity = random.randint(30, 90)

    return (
        f"{city} 今日天气：{condition}，"
        f"气温 {low}~{high}℃，{wind}，相对湿度 {humidity}%（模拟数据）"
    )


# ======================================================================
# 工具 2：数学计算（真实可用）
# ======================================================================
# 运算符映射表：把 AST 语法树节点类型映射到 Python 的对应运算函数
_OPERATORS = {
    ast.Add: operator.add,        # +
    ast.Sub: operator.sub,        # -
    ast.Mult: operator.mul,       # *
    ast.Div: operator.truediv,    # /
    ast.FloorDiv: operator.floordiv,  # //
    ast.Mod: operator.mod,        # %
    ast.Pow: operator.pow,        # **
    ast.USub: operator.neg,       # 一元负号 -
    ast.UAdd: operator.pos,       # 一元正号 +
}


def _safe_eval(node: ast.AST) -> float:
    """
    递归地"安全计算"一个 AST 表达式节点。

    为什么不用 eval()？
      eval("2+3") 确实能算数，但 eval("__import__('os').system('rm -rf /')") 也能执行！
      大模型传来的字符串不可完全信任，直接 eval 存在代码注入风险。
    安全做法：先把字符串解析成 AST（抽象语法树），再逐节点遍历，
    只允许出现"数字 + 四则运算符"，遇到其他任何内容立即抛错拒绝。
    """
    if isinstance(node, ast.Expression):          # 整个表达式的根节点
        return _safe_eval(node.body)
    if isinstance(node, ast.Constant):            # 数字常量（如 3、2.5）
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError(f"不允许的常量: {node.value!r}")
    if isinstance(node, ast.BinOp) and type(node.op) in _OPERATORS:   # 二元运算 a op b
        return _OPERATORS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPERATORS: # 一元运算 op a
        return _OPERATORS[type(node.op)](_safe_eval(node.operand))
    raise ValueError("表达式中包含不允许的元素（只支持数字和 + - * / // % ** 运算）")


@tool
def calculate(expression: str) -> str:
    """计算一个数学表达式的结果。

    当用户提出需要精确计算的数学问题时使用此工具（不要心算，必须调用本工具）。
    支持 + - * / // % ** 运算和括号，例如 "(1 + 2) * 3.5 / 7"。

    Args:
        expression: 数学表达式字符串，例如 "3.5 * (12 + 8)"
    """
    try:
        # ast.parse 把字符串解析成语法树，mode="eval" 表示按"单个表达式"解析
        tree = ast.parse(expression, mode="eval")
        result = _safe_eval(tree)
        return f"{expression} = {result}"
    except (ValueError, SyntaxError, ZeroDivisionError) as e:
        # 出错时把原因返回给大模型，它会自己决定怎么向用户解释或重试
        return f"计算失败：{e}"


# ======================================================================
# 工具 3：时间查询（真实可用，用的是本机系统时间）
# ======================================================================
# 城市名 → IANA 时区名的映射表
_CITY_TIMEZONES = {
    "北京": "Asia/Shanghai",
    "上海": "Asia/Shanghai",
    "东京": "Asia/Tokyo",
    "首尔": "Asia/Seoul",
    "新加坡": "Asia/Singapore",
    "伦敦": "Europe/London",
    "巴黎": "Europe/Paris",
    "莫斯科": "Europe/Moscow",
    "纽约": "America/New_York",
    "洛杉矶": "America/Los_Angeles",
    "悉尼": "Australia/Sydney",
}


@tool
def get_current_time(city: str) -> str:
    """查询指定城市当前的日期和时间。

    当用户询问"现在几点了"、"某城市现在的时间"、日期等问题时使用此工具。

    Args:
        city: 城市名称，例如 "北京"、"纽约"、"伦敦"
    """
    # 找不到的城市默认按北京时间处理
    tz_name = _CITY_TIMEZONES.get(city, "Asia/Shanghai")
    now = datetime.now(ZoneInfo(tz_name))  # 带时区的当前时间
    return f"{city} 当前时间：{now.strftime('%Y-%m-%d %H:%M:%S')}（时区 {tz_name}）"


# ======================================================================
# 工具 4：货币转换（模拟固定汇率）
# ======================================================================
# 模拟汇率表：1 单位该货币 = ? 人民币（真实场景应调用实时汇率 API，如 exchangerate-api）
_EXCHANGE_RATES = {
    "CNY": 1.0,      # 人民币
    "USD": 7.12,     # 美元
    "EUR": 7.85,     # 欧元
    "GBP": 9.05,     # 英镑
    "JPY": 0.048,    # 日元
    "KRW": 0.0052,   # 韩元
    "HKD": 0.91,     # 港币
}


@tool
def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    """把一定金额从一种货币换算成另一种货币。

    当用户询问汇率换算问题时使用此工具，例如"100 美元能换多少人民币"。

    Args:
        amount: 金额数值
        from_currency: 原始货币的三位代码，如 USD、CNY、EUR、JPY
        to_currency: 目标货币的三位代码，如 CNY、JPY、GBP
    """
    from_code = from_currency.upper()
    to_code = to_currency.upper()

    if from_code not in _EXCHANGE_RATES or to_code not in _EXCHANGE_RATES:
        supported = "、".join(_EXCHANGE_RATES)
        return f"不支持的货币，目前仅支持：{supported}"

    # 换算逻辑：先统一折算成人民币，再换算成目标货币
    cny_amount = amount * _EXCHANGE_RATES[from_code]
    result = cny_amount / _EXCHANGE_RATES[to_code]
    return f"{amount} {from_code} ≈ {result:.4f} {to_code}（按模拟固定汇率计算）"


# ======================================================================
# 工具 5：信息搜索（模拟）
# ======================================================================
@tool
def search_information(query: str) -> str:
    """在互联网上搜索信息。

    当用户询问实时性、常识性、你（大模型）不确定或不知道的信息时使用此工具，
    例如新闻、人物资料、产品信息等。

    Args:
        query: 搜索关键词
    """
    # --- 模拟实现：真实场景只需换成下面一行代码 ---
    #   from langchain_tavily import TavilySearch
    #   return TavilySearch(max_results=3).invoke({"query": query})["results"]
    fake_results = (
        f"[模拟搜索结果] 关于「{query}」找到 2 条信息：\n"
        f"1. {query}是近期备受关注的话题，相关讨论热度持续上升，"
        f"多个平台均有相关报道和解读文章。\n"
        f"2. 据模拟百科收录：{query}的背景、发展过程与影响已在词条中详细介绍，"
        f"可供进一步参考。（数据为模拟，仅用于演示工具调用流程）"
    )
    return fake_results


# 汇总成工具列表：create_agent 会把每个工具的"说明书"（名字+描述+参数 schema）
# 发给大模型，模型据此决定何时调用哪个工具
ALL_TOOLS = [get_weather, calculate, get_current_time, convert_currency, search_information]

# LangGraph Agent：初始化模型 + 预构建 ReAct Agent
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

from app.agent.tools import TOOLS
from app.core.config import settings


def _build_model():
    # 惰性创建模型：init_chat_model 会立即校验 API key，
    # 所以不能放在模块顶层（否则 import 就要有 key，测试也过不了）
    return init_chat_model(
        model=settings.llm_model,
        model_provider="openai",  # OpenAI 兼容协议客户端
        api_key=settings.company_api_key,
        base_url=settings.company_base_url,
    )


def build_agent(model_override=None, checkpointer=None):
    """构建一个编译好的 Agent（返回 CompiledStateGraph）。

    参数：
      model_override：测试时注入假模型，避免真调 LLM
      checkpointer：工作流状态持久化器（由调用方创建并管理其连接生命周期）
    生产由 lifespan 传入 AsyncSqliteSaver；测试传入 InMemorySaver。
    """
    # 用到的模型：优先用注入的假模型，否则惰性创建真实模型
    m = model_override if model_override is not None else _build_model()

    # 预构建 ReAct Agent：模型 + 工具 + checkpointer 一步到位
    # ReAct = 思考(Reasoning) + 行动(Acting)：模型决定是否调工具，循环直到给出最终答案
    return create_agent(m, tools=TOOLS, checkpointer=checkpointer)


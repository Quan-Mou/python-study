"""
config.py —— 配置模块
=====================

学习要点：
1. python-dotenv 负责把 .env 文件里的 "KEY=VALUE" 加载到环境变量（os.environ）中，
   这样 API 密钥就不会硬编码在代码里，也不会被提交到 git（.gitignore 已忽略 .env）；
2. langchain.chat_models.init_chat_model 是 LangChain 提供的"统一模型工厂"：
   只需指定 model + model_provider，就能拿到统一的 BaseChatModel 对象，
   以后换模型（比如从 GLM 换成 DeepSeek）只需要改配置，业务代码完全不用动。
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

# .env 文件位于仓库根目录（python-study/.env），和 langchain-learning 项目共用同一份密钥。
# 路径推算：本文件是 .../python-study/smart-assistant/src/smart_assistant/config.py
#   parents[0] = smart_assistant/  parents[1] = src/  parents[2] = smart-assistant/
#   parents[3] = python-study/（仓库根目录，.env 就在这里）

#  __file__是 python内置的一个变量，表示当前脚本的一个路径
_REPO_ROOT = Path(__file__).resolve().parents[3]
# verbose=True 会在加载时打印提示，方便确认到底加载了哪个 .env 文件
load_dotenv(_REPO_ROOT / ".env", verbose=True)


def get_llm():
    """
    根据可用的 API 密钥初始化聊天模型。

    优先级：
    1. 有 COMPANY_API_KEY / COMPANY_BASE_URL → 使用公司 OpenAI 兼容接口（glm-5.3-flash）
    2. 否则使用 DEEPSEEK_API_KEY → 走 DeepSeek 官方接口（deepseek-chat）

    init_chat_model 返回的模型对象实现了统一的接口（invoke / stream / bind_tools ...），
    这正是 LangChain 的核心价值：一套代码适配所有模型厂商。
    """
    company_key = os.getenv("COMPANY_API_KEY")
    company_url = os.getenv("COMPANY_BASE_URL")

    if company_key:
        # model_provider="openai" 表示用 OpenAI 协议访问（大多数国产模型都兼容此协议）
        return init_chat_model(
            model="glm-5.3-flash",
            model_provider="openai",
            api_key=company_key,
            base_url=company_url,
        )

    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    if deepseek_key:
        return init_chat_model(
            model="deepseek-chat",
            model_provider="deepseek",
            api_key=deepseek_key,
        )

    raise RuntimeError(
        "未找到可用的 API 密钥，请在仓库根目录的 .env 中配置 "
        "COMPANY_API_KEY/COMPANY_BASE_URL 或 DEEPSEEK_API_KEY"
    )

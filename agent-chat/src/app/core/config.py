# 应用配置：用 pydantic-settings 从 .env / 环境变量读取，字段名不区分大小写
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# 先把 .env 加载进环境变量（override=True 表示 .env 里的值优先），Settings 才读得到
# python-dotenv 会从当前目录逐级向上查找 .env，所以放根目录或本目录都行
load_dotenv(override=True)


class Settings(BaseSettings):
    # 应用名
    app_name: str = "agent-chat"

    # 业务数据库连接串：MySQL + 异步驱动 aiomysql
    # 默认用占位符（ASCII，避免驱动按 latin-1 编码中文占位符报错），
    # 真实连接串请通过 .env 的 DATABASE_URL 注入（不要写死在源码里）
    database_url: str = (
        "mysql+aiomysql://root:123456@127.0.0.1:3306/agent_chat?charset=utf8mb4"
    )

    # JWT 签名算法
    algorithm: str = "HS256"
    # token 有效期（分钟）
    access_token_expire_minutes: int = 30
    # JWT 签名密钥：生产必须用环境变量注入一段随机值，不能留在代码里
    # （HS256 要求密钥 ≥32 字节，默认占位符已满足长度）
    secret_key: str = "change-me-to-a-long-random-secret-key-please"

    # 大模型配置（公司网关，OpenAI 兼容协议）
    company_api_key: str = "magpie"
    company_base_url: str = "http://127.0.0.1:3425/v1"
    llm_model: str = "workbuddy/deepseek-v4-pro"

    # extra="ignore"：环境变量里出现未知字段时忽略，避免报错
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


# 全局单例，所有模块 import 它拿配置
settings = Settings()

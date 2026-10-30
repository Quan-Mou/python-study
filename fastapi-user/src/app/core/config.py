from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    app_name: str = "fastapi-user"
    database_url: str = "mysql+pymysql://root:123456@127.0.0.1:3306/learn_db?charset=utf8mb4"

    # SettingsConfigDict：pydantic-settings v2 的配置入口（env_file、env_prefix 等），留空即默认行为
    model_config = SettingsConfigDict()


app_settings = AppSettings()

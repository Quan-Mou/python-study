from langchain.agents import create_agent
from dotenv import load_dotenv
import os

from langchain_core.messages import HumanMessage

load_dotenv(verbose=True)
from langchain.chat_models import init_chat_model
def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"


api_key = os.getenv("COMPANY_API_KEY")
base_url = os.getenv("COMPANY_BASE_URL")



model = init_chat_model(
    model="qwen3.7-plus",
    model_provider="openai",
    api_key=api_key,
    base_url=base_url
)


# Run the agent
model.invoke(
    [
        HumanMessage(content="我是谁？")
    ]
)
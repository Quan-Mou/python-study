from dotenv import load_dotenv
import os
load_dotenv(verbose=True)

from langchain_core.messages import SystemMessage, HumanMessage


from langchain.tools import tool



from langchain.chat_models import init_chat_model
from langchain_core.messages import content, SystemMessageChunk
from openai import api_key, base_url




api_key = os.getenv("COMPANY_API_KEY")
base_url = os.getenv("COMPANY_BASE_URL")

model = init_chat_model(
    model="qwen3.7-plus",
    model_provider="openai",
    api_key=api_key,
    base_url=base_url
)


model.invoke("你是谁？")




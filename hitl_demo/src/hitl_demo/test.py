
from dotenv import load_dotenv
import os



from langchain.chat_models import init_chat_model



load_dotenv(override=True)


api_key = os.getenv("COMPANY_API_KEY")
base_url = os.getenv("COMPANY_BASE_URL")

print(api_key)
print(base_url)


model = init_chat_model(
    model="qwen3.7-plus",
    model_provider="openai",
    api_key=api_key,
    api_base=base_url,  # 关键：改用 api_base
)


result = model.invoke("hello ")


print(result)



import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

stream = client.chat.completions.create(
    model="qwen-plus",
    messages=[                                    
        {"role": "system", "content": "你是一个有用的助手。"},
        {"role": "user", "content": "用一句话介绍 Python 的 FastAPI"}
    ],
    stream = True # 开启流式输出                                             
)


for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
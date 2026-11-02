import asyncio

import time

from fastapi import FastAPI

app = FastAPI()


@app.get("/sync")
def sync_api():
    time.sleep(2)
    return {
        "message":"同步调用接口执行完毕"
    }

@app.get('/async')
async def async_api():
    await asyncio.sleep(2)
    return {
        "message": "异步调用接口执行完毕"
    }


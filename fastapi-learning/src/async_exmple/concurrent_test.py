import asyncio
import time
import httpx



async def test1():
    async with httpx.AsyncClient() as client:
        start = time.perf_counter()

        results = await asyncio.gather(
            client.get("http://127.0.0.1:8100/sync"),
            client.get("http://127.0.0.1:8100/sync"),
            client.get("http://127.0.0.1:8100/sync")
        )

        print(f"同步接口耗时：{time.perf_counter() - start}")

        start = time.perf_counter()
        results =  await asyncio.gather(
            client.get("http://127.0.0.1:8100/async"),
            client.get("http://127.0.0.1:8100/async"),
            client.get("http://127.0.0.1:8100/async")
        )

        print(f"异步接口耗时：{time.perf_counter() - start}")

if __name__ == "__main__":
    asyncio.run(test1())


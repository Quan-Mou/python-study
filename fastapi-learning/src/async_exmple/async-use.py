import asyncio


async def task1():
    print("任务1开始")
    await asyncio.sleep(2)
    print("任务1结束")

# 异步不是让代码执行速度变快，而是在程序IO阻塞等待时能做处理其他任务

async def task2():
    print("任务2开始")
    await asyncio.sleep(2)
    print("任务2结束")


# 协程是Python的异步执行的基本单位
# 定义一个普通函数
def hello1():
    pass

# 定义一个异步函数
async def hello2():
    pass


# 普通函数和异步函数有一个重要的区别：
# 普通函数返回的是函数的返回值
# 异步函数返回的是一个协程对象，并没有真正执行函数的内部逻辑,需要通过await或者事件循环来执行它

"""
    async_exmple def ：定义协程函数
    调用异步函数：创建协程对象
    await：等待协程或者其他Awaitable完成
    asyncio.run() 创建并执行事件循环，执行顶层协程
    asyncio.gather() ：并发调度多个Awaitable


    
"""


async def main():
    await asyncio.gather(
        task1(),
        task2()
    )

if __name__ == "__main__":
    # 创建事件循环，运行协程，清理循环。它是异步程序的入口
    asyncio.run(main())




# Python 学习工程

父目录下多个独立项目，共用一个 git 仓库。

## 项目列表

| 目录 | 说明 |
|------|------|
| [python-basics/](python-basics/) | Python 基础语言学习示例（01-18 编号脚本） |
| [langchain-learning/](langchain-learning/) | LangChain 学习项目：模型调用、Prompt、Agent、工具调用、结构化输出、LangSmith 可观测性、多模态 |
| [langgraph-learning/](langgraph-learning/) | LangGraph 学习项目：StateGraph、Edge、Checkpointer 持久化、时间旅行、Memory、中断（HITL）、容错恢复 |
| [smart-assistant/](smart-assistant/) | 多功能智能助手：基于 LangChain 的工具调用（天气/数学/时间/货币转换/信息搜索） |
| [hitl_demo/](hitl_demo/) | Human-In-The-Loop 演示项目（基于 LangGraph） |

## 使用方式

各项目独立使用 uv 管理依赖，进入对应目录操作即可：

```bash
# 示例：进入 langgraph-learning
cd langgraph-learning
uv sync
uv run python -m langgraph_learning

# 示例：运行 python-basics 的某个脚本
cd python-basics
uv run 01.py
```

## 公共配置

根目录 `.env` 存放跨项目共用的 API Key（DeepSeek / Company / LangSmith 等），各子项目按需读取。敏感信息已通过 `.gitignore` 排除，不会提交到仓库。


# 随记


事件循环：可以理解为异步任务的调度中心：
他负责：
1. 接收运行的协程
2.调度协程运行
3. 当协程遇到await时，暂停当前协程
4. 调度其他已经就绪的协程
5. 等待之前的任务完成后恢复执行



异步操作数据库的并发问题：
一个AsyncSession不能被多个并发任务共享，比如：
async def main():
   await asyncio.gather(
        query_user(db),
        query_order(db)
    )

两个协程同时使用一个session，可能导致事务冲突和并发错误。
正确的方式是每个并发创建自己的session。
~~~python
async def query_user():
    await with AsyncSessionLocal() as db:
        pass
    

async def query_order():
    await with AsyncSessionLocal() as db:
        pass
    
    
async def main():
    await asyncio.gather(
        query_user(),
        query_order()
    )

~~~
- Engine可以在应用内共享
- async async_Sessionmaker可以在应用内共享
- 每个独立请求或并发请求应该使用自己的AsyncSession
- 不要将一个Session全局保存，然后供多个请求使用




后台任务与生命周期：
- BackgroundTask：请求返回后，再后台执行一些任务，不用等待返回在执行下一步
- LifeSpan：管理FastAPI应用启动和关闭时的资源


LifeSpan生命周期：
- 数据库连接池
- httpx异步客户端
- Redis连接
- AI模型客户端
- 其他共享资源
这些资源不应该在每个请求中都重复创建。
每次重复创建会带来额外的创建和销毁开销
合理的方式是：
- 应用启动时初始化客户端
- 各个请求复用客户端
- 应用关闭时释放客户端

使用asynccontextmanager实现LifeSpan


pytest:python中的自动化框架
在java中可能使用过junit，spring boot test



流式响应：
流式响应和json响应的区别：
json响应：客户端需要等到响应数据准备好才能拿到完整json数据
流式响应：客户端可以逐步接受生成的数据，而不必等待全部完成


media_type:
- text/plain :浏览器/客户端 这是文本类型，不做其他处理
- application/json：浏览器/客户端知道这是json，可以直接解析成对象
- text/event-stream

SSE(Server-Send Events):服务端发送事件
是一种基于http的服务器向客户端单向发送数据的机制
- 基于HTTP
- 数据以事件流的形式传输
- 服务端向客户端持续推送数据
- 通常使用 text/event-stream
- 浏览器可以使用EventSource接收事件

适合AI大模型回答、系统通知、实时任务进度、Agent任务过程展示


SSE和Websocket不一样：
- sse是服务端向客户端单向推送数据，websocket支持双向通信


SSE适合服务器单向推送，如果服务器和客户端都需要发送消息，则需要使用Websocket
- 实时通讯
- 在线客服
- 实时协作
- 双向实时控制
- 实时语音交互

HTTP：请求/响应，通常请求结束后关闭
SSE:服务器端单向推送，持续HTTP连接
Websocket：双向通信，持续连接


















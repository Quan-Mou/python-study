# agent-chat

综合学习项目：把 FastAPI 学过的知识点串成一个可运行的 AI 对话服务。

## 功能清单

| # | 功能 | 实现 |
|---|------|------|
| 1 | 用户注册 / 登录 / JWT 认证 | `pwdlib[argon2]` 哈希密码 + `pyjwt` 签发/校验 token + `HTTPBearer` 依赖 |
| 2 | AI 对话接口 | `POST /api/chat`（需登录） |
| 3 | LangGraph 执行 Agent | `langgraph.prebuilt.create_react_agent` + 两个工具（查时间 / 算数） |
| 4 | SSE 流式输出 | `StreamingResponse` + `graph.astream(stream_mode="messages")` 逐 token 下发 |
| 5 | MySQL 保存对话记录 | `aiomysql` + SQLAlchemy 异步，users / conversations / messages 三张表 |
| 6 | Checkpointer 保存工作流状态 | `langgraph-checkpoint-sqlite` 持久化到 `checkpoints.sqlite`（可按需换 Postgres） |
| 7 | pytest 测试核心接口 | `tests/`：认证 + 聊天（假模型 + 内存 SQLite，不碰真 LLM/真库） |

## 目录结构

```
agent-chat/
├── src/app/
│   ├── main.py              # 应用入口（create_app 工厂，便于测试注入假依赖）
│   ├── run.py               # uv run dev 启动
│   ├── core/                # config 配置 / security 认证 / database 数据库 / deps 鉴权依赖
│   ├── models/              # ORM：user / conversation / message
│   ├── schemas/             # 请求/响应模型
│   ├── repositories/        # 数据访问层（DAO）
│   ├── services/            # 业务层：auth_service / chat_service（SSE 流式）
│   ├── api/                 # 路由：auth / chat
│   └── agent/               # LangGraph：tools 工具 + graph 图构建
└── tests/                   # pytest：conftest 夹具 + 认证/聊天测试
```

## 快速开始

```powershell
# 1. 安装依赖
uv sync

# 2. 准备配置：复制 .env.example 为 .env，填数据库密码 + 大模型 key
#    （先建库：CREATE DATABASE agent_chat CHARACTER SET utf8mb4;）

# 3. 启动（二选一）
uv run python -m uvicorn app.main:app --reload --port 8082
uv run dev        # 等价，端口写死在 run.py 里是 8082

# 4. 跑测试（不依赖真 MySQL / 真 LLM）
uv run pytest -v
```

## 接口一览（Swagger：http://127.0.0.1:8082/docs）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/auth/register` | 注册，body `{username, password, email?}` |
| POST | `/api/auth/login` | 登录，body `{username, password}` → 返回 `access_token` |
| GET | `/api/auth/me` | 当前用户（需 `Authorization: Bearer <token>`） |
| POST | `/api/chat` | 对话，body `{content, thread_id?}` → SSE 流 |
| GET | `/api/chat/history/{thread_id}` | 查某会话历史（需登录、且属本人） |

SSE 事件格式（每条 `data: {...}` + 空行）：

```json
{"type": "token", "content": "..."}   // 文本增量
{"type": "tool", "name": "..."}       // 模型调工具
{"type": "done", "content": "..."}    // 结束，附完整回复
```

## 关键设计说明

- **业务库用 MySQL、状态存 SQLite**：你要求业务库用 MySQL（`DATABASE_URL` 配置 `mysql+aiomysql://...`）；LangGraph Checkpointer 选了官方 `langgraph-checkpoint-sqlite`（持久化到文件、零额外服务）。若想换成 Postgres checkpointer，`langgraph-learning` 已装过 `langgraph-checkpoint-postgres`，把 `graph.py` 里的 `AsyncSqliteSaver` 换成 `AsyncPostgresSaver` 即可。
- **`create_app()` 工厂**：生产走真实模型 + MySQL；测试注入 `FakeListChatModel` + 内存 SQLite，互不影响。
- **流式与落库分离**：请求级 session 先存 user 消息；流式生成器用独立 session 在结束后存 assistant 消息，避免长连接占住请求 session。

# smart-assistant 多功能智能助手

基于 **Python + LangChain（v1.x `create_agent`）** 的命令行智能助手，用于学习 LangChain 的工具调用（Tool Calling）机制。

## 功能

| 工具 | 功能 | 实现方式 |
|---|---|---|
| `get_weather` | 🌤️ 天气查询 | 模拟数据 |
| `calculate` | 🧮 数学计算 | AST 安全求值（真实可用） |
| `get_current_time` | 🕐 时间查询 | 本机系统时间 + 时区（真实可用） |
| `convert_currency` | 💱 货币转换 | 模拟固定汇率 |
| `search_information` | 🔍 信息搜索 | 模拟搜索结果 |

## 运行

```bash
cd smart-assistant
uv sync                 # 安装依赖（密钥复用仓库根目录的 .env）
uv run smart-assistant  # 启动命令行交互
```

## 项目结构

```
smart-assistant/
├── pyproject.toml              # 项目与依赖配置
└── src/smart_assistant/
    ├── config.py               # 加载 .env + init_chat_model 初始化模型
    ├── tools.py                # 5 个工具（@tool 装饰器，重点学习文件）
    └── main.py                 # CLI 交互入口（create_agent + stream）
```

## 学习要点

1. **@tool 装饰器**：函数的 docstring 就是给大模型看的"工具说明书"
2. **create_agent(model, tools, system_prompt)**：三件套创建 Agent，内部由 LangGraph 自动调度"思考 → 调工具 → 观察 → 再思考"循环
3. **stream_mode="values"**：实时打印 Agent 每一步的消息，可视化工具调用过程
4. **init_chat_model**：统一模型接口，一行换厂商（GLM / DeepSeek）

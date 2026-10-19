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

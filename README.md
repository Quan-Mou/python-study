# Python 学习工程

父目录下多个独立项目，共用一个 git 仓库。

## 项目列表

| 目录 | 说明 |
|------|------|
| [python-basics/](python-basics/) | Python 基础语言学习示例（01-18 编号示例） |
| [langchain-learning/](langchain-learning/) | LangChain 学习项目 |

## 使用方式

各项目独立使用 uv 管理依赖，进入对应目录操作即可：

```bash
cd python-basics
uv run 01.py

cd langchain-learning
uv add langchain
uv run python -m langchain_learning
```

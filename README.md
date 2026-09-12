# python-study

Python 学习笔记与练习工程，从基础语法到面向对象、多线程、网络请求、常用标准库与第三方库（pandas、OpenAI SDK），以及一个 HTML 评论解析 + MySQL 入库的实战小项目。

## 环境

- Python >= 3.10
- 包管理器：[uv](https://docs.astral.sh/uv/)

```bash
uv sync          # 安装依赖
python main.py   # 运行示例
```

## 目录结构

| 文件 | 内容 |
| --- | --- |
| `01.py` | 打印、单行/多行注释 |
| `02.py` | 列表、元组、字典、集合等容器类型 |
| `03.py` | 函数定义与 `__name__` |
| `04.py` | 迭代器 `iter()` / `next()` |
| `05.py` | 类型注解（type hints） |
| `06.py` | 类与对象：类变量、构造函数、实例方法 |
| `07.py` | 魔术方法：`__str__`、`__repr__`、运算符重载 |
| `08.py` | `@property` 实现 getter / setter |
| `09.py` | 常用标准库：`os`、`time`、`re`、`json` 等 |
| `10.py` | `mysql-connector` 操作数据库，含 JSON 序列化处理 |
| `11.py` | 多线程：`_thread` 与 `threading` 模块的使用 |
| `12.py` | `requests` 发送 HTTP 请求，获取状态码与 JSON 响应 |
| `13.py` | 通过 OpenAI 兼容接口调用阿里云百炼（DashScope）大模型，支持流式输出 |
| `14.py` | `pandas` 基础：创建 DataFrame / Series 及常用操作 |
| `15.py` | lambda 表达式：定义、多参数、配合 `sorted()` 的 `key` 使用 |
| `main.py` / `utils.py` | 模块导入与 `if __name__ == "__main__"` 示例 |
| `documentParse.py` | 解析抖音评论 HTML，提取一级/二级评论并写入 MySQL |
| `new.py` | `documentParse.py` 的改进版，输出树形结构评论数据 |
| `src/python_study/` | 通过 `pyproject.toml` 打包的入口模块 |

## 依赖

```
mysql-connector-python   # 10.py 数据库操作
openai                   # 13.py 调用大模型 API
pandas                   # 14.py 数据分析
requests                 # 12.py HTTP 请求
pymysql                  # documentParse.py / new.py 数据库操作
beautifulsoup4           # documentParse.py / new.py 解析 HTML
```

## 说明

- 本工程为个人学习用途，代码中保留了大量中文注释，便于对照 Java 等语言理解 Python 的特性。
- 部分示例需要自行配置后运行：
  - `10.py`、`documentParse.py`、`new.py`：需修改代码中的 MySQL 连接信息（host / user / password / database）。
  - `12.py`：需在 `params` 中填入自己的 API `access_key`。
  - `13.py`：需设置环境变量 `DASHSCOPE_API_KEY`（阿里云百炼 API Key）。

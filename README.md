# OpenKylin 开放麒麟

> 轻量级模块化 AI 智能体框架

[![Python Version](https://img.shields.io/badge/python-3.10+-blue)](https://pypi.org/project/openkylin/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## 简介

OpenKylin（开放麒麟）是一个轻量级、模块化的 AI 智能体框架，源自麒麟传说。极简内核、清晰模块边界、插件化设计，助您轻松构建高效智能的垂直领域 AI 助手。

## 特性

- **多消息渠道集成**：统一抽象层支持钉钉、飞书、企业微信、Telegram、Discord、Slack 等主流平台
- **工具/插件系统**：基于 entry_points 的动态插件加载机制，兼容 OpenClaw SKILL.md 格式
- **记忆/上下文管理**：短期会话记忆 + 长期向量存储分离设计
- **多模型支持**：OpenAI、Anthropic Claude、Ollama（本地）、DeepSeek、通义千问等
- **RAG 知识库**：简化版向量检索 + 生成，支持私有知识库
- **工作流/Agent 编排**：基于 DAG 的任务编排引擎
- **多客户端支持**：Python CLI、Web UI、移动端（通过 IM 渠道接入）

## 与 OpenClaw 对比

| 特性 | OpenClaw | OpenKylin |
|------|----------|-----------|
| 核心依赖 | Node.js 22+ | Python 3.10+ |
| 架构 | Monorepo 20+ 包 | 核心 + 独立插件 |
| 复杂度 | 高 | 轻量简约 |
| Skill 兼容 | 原生支持 | 兼容加载 |
| 资源占用 | 较高 | 低 |

## 快速开始

### 安装

```bash
pip install openkylin
```

### 配置文件

创建 `.env` 文件：

```bash
# 模型配置
OPENAI_API_KEY=your-api-key
OPENKYLIN_PROVIDER=openai  # 或 ollama
OPENKYLIN_MODEL=gpt-4

# 系统提示
OPENKYLIN_SYSTEM_PROMPT=你是一个有用的AI助手。
```

### 使用 CLI

```bash
openkylin
```

### 代码示例

```python
import asyncio
from openkylin import Agent, Message
from openkylin.extensions.providers.openai import OpenAIProvider

async def main():
    # 创建模型供应商
    provider = OpenAIProvider()

    # 创建 Agent
    agent = Agent(provider=provider)

    # 对话
    response = await agent.chat("你好，介绍一下自己")
    print(response)

asyncio.run(main())
```

## 项目结构

```
openkylin/
├── core/                    # 核心框架
│   ├── agent.py            # Agent 引擎 (ReAct 模式)
│   ├── message.py          # 统一消息抽象
│   ├── event.py           # 事件总线
│   ├── router.py           # 消息路由器
│   └── plugin.py           # 插件管理系统
├── extensions/             # 扩展模块
│   ├── channels/          # 消息渠道插件
│   ├── tools/             # 工具插件
│   ├── memory/            # 记忆存储
│   └── providers/         # 模型供应商
├── services/               # 服务层
│   ├── rag/              # RAG 引擎
│   └── workflow/          # 工作流引擎
├── clients/               # 客户端
│   └── cli/              # Python CLI
└── examples/              # 示例代码
```

## 文档

更多文档请访问 [docs/](docs/)

## 许可证

MIT License - see [LICENSE](LICENSE)

## 贡献

欢迎贡献！请提交 Issue 或 Pull Request。

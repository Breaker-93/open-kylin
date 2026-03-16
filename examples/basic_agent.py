"""基础 Agent 示例 - Basic Agent Example

展示如何使用 OpenKylin 构建一个简单的 AI 助手。
"""

import asyncio
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from pathlib import Path

from openkylin.core.agent import AgentConfig, ReActAgent
from openkylin.core.event import EventBus
from openkylin.core.message import Message, Role
from openkylin.extensions.providers.openai import OpenAIProvider
from openkylin.extensions.providers.ollama import OllamaProvider
from openkylin.extensions.tools.registry import ToolRegistry
from openkylin.extensions.tools.base import Tool, ToolResult


# 自定义工具示例
class CalculatorTool(Tool):
    """计算器工具"""

    @property
    def name(self) -> str:
        return "calculator"

    @property
    def description(self) -> str:
        return "执行数学计算，支持加、减、乘、除"

    def get_parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "数学表达式，如 2+3*4"
                }
            },
            "required": ["expression"]
        }

    async def execute(self, expression: str, **kwargs) -> ToolResult:
        """执行计算"""
        try:
            # 安全的表达式计算
            allowed_chars = set("0123456789+-*/.() ")
            if not all(c in allowed_chars for c in expression):
                return ToolResult(success=False, error="Invalid characters in expression")

            result = eval(expression)
            return ToolResult(success=True, result=str(result))
        except Exception as e:
            return ToolResult(success=False, error=str(e))


async def main():
    """主函数"""
    # 创建事件总线
    event_bus = EventBus()

    # 创建模型供应商（可选择 OpenAI 或 Ollama）
    # provider = OllamaProvider()  # 使用本地 Ollama
    provider = OpenAIProvider(
        api_key=os.getenv("OPENAI_API_KEY")
    )

    # 创建工具注册表
    tool_registry = ToolRegistry()
    tool_registry.register(CalculatorTool())

    # 创建 Agent 配置
    config = AgentConfig(
        name="assistant",
        model="gpt-4",
        system_prompt="""你是一个有用的AI助手。
你有一个计算器工具，可以帮助用户进行数学计算。
当用户需要计算时，使用 calculator 工具。""",
        max_steps=5,
    )

    # 创建 Agent
    agent = ReActAgent(
        config=config,
        provider=provider,
        tool_registry=tool_registry,
        event_bus=event_bus,
    )

    # 对话示例
    print("=== OpenKylin Basic Agent Demo ===\n")

    # 示例 1: 普通对话
    print("User: 你好，请介绍一下自己")
    message1 = Message(role=Role.USER, content="你好，请介绍一下自己")
    response1 = await agent.run(message1)
    print(f"Assistant: {response1.content}\n")

    # 示例 2: 使用工具
    print("User: 请帮我计算 123 * 456 + 789")
    message2 = Message(
        role=Role.USER,
        content="请帮我计算 123 * 456 + 789",
    )
    response2 = await agent.run(message2)
    print(f"Assistant: {response2.content}\n")

    # 显示对话历史
    print("=== Conversation History ===")
    for msg in agent.get_history():
        role = msg.role.value if hasattr(msg.role, 'value') else msg.role
        print(f"{role}: {msg.content[:80]}{'...' if len(msg.content) > 80 else ''}")


if __name__ == "__main__":
    from pathlib import Path
    asyncio.run(main())

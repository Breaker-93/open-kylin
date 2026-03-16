"""CLI 主程序 - Command Line Interface

OpenKylin 命令行客户端。
"""

import asyncio
import os
import sys
from pathlib import Path

import aiohttp
from dotenv import load_dotenv

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from openkylin import __version__
from openkylin.core.agent import AgentConfig, ReActAgent
from openkylin.core.event import EventBus
from openkylin.core.message import Message, Role
from openkylin.extensions.channels.console import ConsoleChannel
from openkylin.extensions.providers.openai import OpenAIProvider
from openkylin.extensions.providers.ollama import OllamaProvider
from openkylin.extensions.tools.registry import ToolRegistry


class OpenKylinCLI:
    """OpenKylin CLI 客户端"""

    def __init__(self):
        self._event_bus = EventBus()
        self._agent = None
        self._running = False
        self._session_id = "cli_session"

    async def initialize(self) -> None:
        """初始化"""
        # 加载环境变量
        load_dotenv()

        # 创建模型供应商
        provider = self._create_provider()

        # 创建工具注册表
        tool_registry = ToolRegistry()

        # 创建 Agent
        config = AgentConfig(
            name="assistant",
            model=os.getenv("OPENKYLIN_MODEL", "gpt-4"),
            system_prompt=os.getenv(
                "OPENKYLIN_SYSTEM_PROMPT",
                "You are a helpful AI assistant."
            ),
            max_steps=int(os.getenv("OPENKYLIN_MAX_STEPS", "10")),
        )

        self._agent = ReActAgent(
            config=config,
            provider=provider,
            tool_registry=tool_registry,
            event_bus=self._event_bus,
        )

    def _create_provider(self):
        """创建模型供应商"""
        provider_type = os.getenv("OPENKYLIN_PROVIDER", "openai")

        if provider_type == "ollama":
            return OllamaProvider()
        else:
            return OpenAIProvider()

    async def run(self) -> None:
        """运行 CLI"""
        await self.initialize()
        self._running = True

        print(f"OpenKylin CLI v{__version__}")
        print("Type 'quit' or 'exit' to exit\n")

        # 显示系统提示
        print(f"System: {self._agent._config.system_prompt}\n")

        while self._running:
            try:
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ["quit", "exit"]:
                    break

                # 创建消息
                message = Message(
                    role=Role.USER,
                    content=user_input,
                    channel="console",
                )

                # 处理消息
                response = await self._agent.run(message)

                # 显示响应
                print(f"\nAssistant: {response.content}\n")

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")

        print("\nGoodbye!")

    async def chat_once(self, message: str) -> str:
        """单次对话"""
        if not self._agent:
            await self.initialize()

        msg = Message(
            role=Role.USER,
            content=message,
            channel="console",
        )

        response = await self._agent.run(msg)
        return response.content


async def main():
    """主入口"""
    cli = OpenKylinCLI()
    await cli.run()


if __name__ == "__main__":
    asyncio.run(main())

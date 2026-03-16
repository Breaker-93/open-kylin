"""控制台渠道 - Console Channel

用于命令行交互的简单渠道。
"""

import asyncio
from typing import Any

from openkylin.core.message import Message, Role
from openkylin.extensions.channels.base import Channel, ChannelConfig


class ConsoleChannel(Channel):
    """控制台渠道

    支持命令行输入输出，用于本地测试和开发。
    """

    def __init__(self, config: ChannelConfig | None = None):
        if config is None:
            config = ChannelConfig(name="console")
        super().__init__(config)
        self._input_queue: asyncio.Queue[Message] = asyncio.Queue()
        self._output_queue: asyncio.Queue[Message] = asyncio.Queue()

    @property
    def metadata(self):
        from openkylin.core.plugin import PluginMetadata, PluginType
        return PluginMetadata(
            name="console",
            plugin_type=PluginType.CHANNEL,
            description="Console channel for CLI interaction",
        )

    async def connect(self) -> None:
        """启动控制台监听"""
        self._running = True
        # 启动输入监听协程
        asyncio.create_task(self._read_input())

    async def disconnect(self) -> None:
        """断开连接"""
        self._running = False

    async def send(self, message: Message) -> None:
        """发送消息到控制台"""
        print(f"\n🤖 Assistant: {message.content}\n")
        print("> ", end="")

    async def receive(self) -> Message:
        """从控制台接收消息"""
        return await self._input_queue.get()

    async def _read_input(self) -> None:
        """读取控制台输入"""
        print("> ", end="", flush=True)
        while self._running:
            try:
                line = await asyncio.get_event_loop().run_in_executor(
                    None, input, ""
                )
                if line.strip():
                    message = Message(
                        role=Role.USER,
                        content=line.strip(),
                        channel="console",
                    )
                    await self._input_queue.put(message)
            except EOFError:
                break
            except Exception as e:
                print(f"Input error: {e}")

    async def handle_input(self, text: str) -> Message:
        """手动处理输入（用于非交互式环境）"""
        message = Message(
            role=Role.USER,
            content=text,
            channel="console",
        )
        return message


class InteractiveConsole(ConsoleChannel):
    """交互式控制台渠道

    支持更丰富的交互功能，如命令补全、历史记录等。
    """

    def __init__(self):
        super().__init__()
        self._history: list[str] = []
        self._history_index = -1

    async def send(self, message: Message) -> None:
        """发送带格式的消息"""
        content = message.content
        # 简单格式化
        if message.role == Role.ASSISTANT:
            print(f"\n\033[96m🤖\033[0m {content}\n")
        else:
            print(f"\n\033[93m👤\033[0m {content}\n")
        print("> ", end="")

    def get_history(self) -> list[str]:
        """获取命令历史"""
        return self._history.copy()

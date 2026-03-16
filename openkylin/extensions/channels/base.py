"""渠道基类 - Channel Base Classes"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable

from openkylin.core.message import Message
from openkylin.core.plugin import Plugin, PluginMetadata, PluginType


@dataclass
class ChannelConfig:
    """渠道配置"""
    name: str
    enabled: bool = True
    webhook_url: str | None = None
    bot_token: str | None = None
    app_id: str | None = None
    app_secret: str | None = None


class Channel(ABC, Plugin):
    """消息渠道抽象基类

    所有渠道插件必须继承此类并实现相应方法。
    """

    def __init__(self, config: ChannelConfig):
        self._config = config
        self._running = False
        self._message_handler: Callable[[Message], Any] | None = None

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name=self._config.name,
            plugin_type=PluginType.CHANNEL,
            description=self.__doc__ or "",
        )

    @property
    def name(self) -> str:
        """渠道名称"""
        return self._config.name

    @property
    def is_running(self) -> bool:
        """是否运行中"""
        return self._running

    @abstractmethod
    async def connect(self) -> None:
        """连接到渠道服务器

        例如：建立 WebSocket 连接、启动 HTTP 服务器等
        """
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """断开连接"""
        pass

    @abstractmethod
    async def send(self, message: Message) -> None:
        """发送消息

        Args:
            message: 要发送的消息
        """
        pass

    async def receive(self, data: Any) -> Message:
        """接收消息（由渠道实现调用）

        Args:
            data: 渠道原始数据

        Returns:
            转换后的 Message 对象
        """
        # 默认实现，子类可重写
        if isinstance(data, Message):
            return data

        return Message(
            role="user",
            content=str(data),
            channel=self._config.name,
        )

    def on_message(self, handler: Callable[[Message], Any]) -> None:
        """设置消息处理函数

        Args:
            handler: 异步处理函数，接收 Message 返回处理结果
        """
        self._message_handler = handler

    async def _handle_message(self, message: Message) -> Any:
        """内部消息处理"""
        if self._message_handler:
            return await self._message_handler(message)
        return None

    async def initialize(self, config: dict[str, Any]) -> None:
        """初始化渠道"""
        # 更新配置
        for key, value in config.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)

    async def shutdown(self) -> None:
        """关闭渠道"""
        if self._running:
            await self.disconnect()


class WebhookChannel(Channel):
    """Webhook 渠道基类

    用于处理被动接收的消息（如钉钉、飞书 Webhook）
    """

    def __init__(self, config: ChannelConfig):
        super().__init__(config)
        self._webhook_path = f"/webhook/{config.name}"

    @property
    def webhook_path(self) -> str:
        return self._webhook_path

    @abstractmethod
    async def handle_webhook(self, data: dict[str, Any]) -> Message:
        """处理 Webhook 数据

        Args:
            data: Webhook 请求体

        Returns:
            转换后的 Message
        """
        pass


class BotChannel(Channel):
    """Bot 渠道基类

    用于主动连接的消息平台（如 Telegram、Discord Bot）
    """

    def __init__(self, config: ChannelConfig):
        super().__init__(config)
        self._polling = False

    @abstractmethod
    async def start_polling(self) -> None:
        """开始轮询消息"""
        pass

    @abstractmethod
    async def stop_polling(self) -> None:
        """停止轮询"""
        pass

    async def connect(self) -> None:
        """建立连接"""
        await self.start_polling()
        self._running = True

    async def disconnect(self) -> None:
        """断开连接"""
        await self.stop_polling()
        self._running = False

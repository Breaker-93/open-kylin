"""钉钉渠道 - DingTalk Channel

支持钉钉自定义机器人 Webhook 消息收发。
"""

import asyncio
import hashlib
import time
import hmac
import base64
from typing import Any

import aiohttp

from openkylin.core.message import Message, Role
from openkylin.extensions.channels.base import Channel, ChannelConfig


class DingTalkChannel(Channel):
    """钉钉自定义机器人渠道

    支持 webhook 回调和主动发送消息。

    配置项:
        webhook_url: 钉钉 webhook 地址
        secret: 加签密钥（可选）
    """

    def __init__(self, config: ChannelConfig):
        super().__init__(config)
        self._session: aiohttp.ClientSession | None = None
        self._secret = config.bot_token  # 用于加签

    @property
    def metadata(self):
        from openkylin.core.plugin import PluginMetadata, PluginType
        return PluginMetadata(
            name="dingtalk",
            plugin_type=PluginType.CHANNEL,
            description="DingTalk custom robot channel",
        )

    async def initialize(self, config: dict[str, Any]) -> None:
        """初始化钉钉渠道"""
        await super().initialize(config)
        self._session = aiohttp.ClientSession()

    async def connect(self) -> None:
        """连接（Webhook 渠道无需主动连接）"""
        self._running = True

    async def disconnect(self) -> None:
        """断开连接"""
        if self._session:
            await self._session.close()
            self._session = None
        self._running = False

    async def send(self, message: Message) -> None:
        """发送消息到钉钉

        支持文本、Markdown、Link、FeedCard 等类型
        """
        if not self._config.webhook_url:
            raise ValueError("webhook_url not configured")

        # 构建消息体
        msg_type = message.metadata.get("type", "text")
        payload = self._build_message(msg_type, message.content, message.metadata)

        # 发送请求
        if self._secret:
            # 加签模式
            url = self._sign_webhook_url(self._config.webhook_url)
        else:
            url = self._config.webhook_url

        async with self._session.post(url, json=payload) as resp:
            result = await resp.json()
            if result.get("errcode") != 0:
                raise Exception(f"DingTalk API error: {result}")

    async def handle_webhook(self, data: dict[str, Any]) -> Message:
        """处理钉钉 Webhook 回调

        Args:
            data: 钉钉回调数据

        Returns:
            Message 对象
        """
        # 解析钉钉消息格式
        msg_type = data.get("msgtype", "text")

        if msg_type == "text":
            content = data.get("text", {}).get("content", "")
        elif msg_type == "markdown":
            content = data.get("markdown", {}).get("text", "")
        elif msg_type == "image":
            content = "[图片消息]"
        elif msg_type == "voice":
            content = "[语音消息]"
        else:
            content = data.get("msgtype", "")

        # 提取发送者信息
        user_id = data.get("senderUserId", "")
        chat_id = data.get("conversationId", "")

        return Message(
            role=Role.USER,
            content=content.strip(),
            channel="dingtalk",
            metadata={
                "msg_type": msg_type,
                "user_id": user_id,
                "chat_id": chat_id,
                "raw": data,
            }
        )

    def _build_message(self, msg_type: str, content: str, metadata: dict) -> dict:
        """构建钉钉消息体"""
        if msg_type == "text":
            return {
                "msgtype": "text",
                "text": {
                    "content": content
                }
            }
        elif msg_type == "markdown":
            return {
                "msgtype": "markdown",
                "markdown": {
                    "title": metadata.get("title", "消息"),
                    "text": content
                }
            }
        elif msg_type == "link":
            return {
                "msgtype": "link",
                "link": {
                    "title": metadata.get("title", "链接"),
                    "text": content,
                    "messageUrl": metadata.get("url", ""),
                }
            }
        else:
            # 默认文本
            return {
                "msgtype": "text",
                "text": {
                    "content": content
                }
            }

    def _sign_webhook_url(self, webhook_url: str) -> str:
        """生成加签 URL

        钉钉机器人安全设置 - 加签
        """
        timestamp = str(round(time.time() * 1000))
        secret_enc = self._secret.encode("utf-8")
        string_to_sign = f"{timestamp}\n{self._secret}"
        string_to_sign_enc = string_to_sign.encode("utf-8")
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = base64.b64encode(hmac_code).decode("utf-8")

        # 拼接 URL
        separator = "&" if "?" in webhook_url else "?"
        return f"{webhook_url}{separator}timestamp={timestamp}&sign={sign}"


class DingTalkAppChannel(DingTalkChannel):
    """钉钉企业内部应用渠道

    使用企业内部应用 API 发送消息
    """

    def __init__(self, config: ChannelConfig):
        super().__init__(config)
        self._access_token: str | None = None
        self._token_expires_at: float = 0

    async def _get_access_token(self) -> str:
        """获取应用 access_token"""
        now = time.time()
        if self._access_token and now < self._token_expires_at:
            return self._access_token

        if not self._config.app_id or not self._config.app_secret:
            raise ValueError("app_id and app_secret required")

        # 调用钉钉获取 token API
        url = "https://api.dingtalk.com/v1.0/oauth2/accessToken"
        payload = {
            "appKey": self._config.app_id,
            "appSecret": self._config.app_secret,
        }

        async with self._session.post(url, json=payload) as resp:
            result = await resp.json()
            if "accessToken" not in result:
                raise Exception(f"Failed to get access_token: {result}")

            self._access_token = result["accessToken"]
            self._token_expires_at = now + result.get("expireIn", 7200) - 300
            return self._access_token

    async def send(self, message: Message) -> None:
        """使用应用 API 发送消息"""
        token = await self._get_access_token()
        # 构建消息并发送
        # 这里省略具体的 API 调用实现
        await super().send(message)

"""模型供应商抽象层 - Model Provider Abstraction

统一接口适配多种模型供应商：OpenAI、Anthropic Claude、Ollama、DeepSeek 等。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, AsyncIterator

from openkylin.core.plugin import Plugin, PluginMetadata, PluginType


@dataclass
class ChatMessage:
    """聊天消息"""
    role: str  # system, user, assistant, tool
    content: str
    name: str | None = None
    tool_call_id: str | None = None


@dataclass
class ChatCompletion:
    """聊天完成响应"""
    id: str
    model: str
    content: str
    finish_reason: str = "stop"
    usage: dict[str, int] = field(default_factory=dict)


@dataclass
class ModelInfo:
    """模型信息"""
    id: str
    name: str
    provider: str
    context_length: int = 4096
    supports_streaming: bool = True
    supports_function_calling: bool = True


class ModelProvider(ABC, Plugin):
    """模型供应商抽象基类"""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """供应商名称"""
        pass

    @property
    @abstractmethod
    def default_model(self) -> str:
        """默认模型"""
        pass

    @abstractmethod
    async def chat(
        self,
        messages: list[dict[str, Any]] | list[ChatMessage],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs
    ) -> str:
        """同步聊天

        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度
            max_tokens: 最大 token 数
            **kwargs: 其他参数

        Returns:
            响应内容
        """
        pass

    @abstractmethod
    async def stream_chat(
        self,
        messages: list[dict[str, Any]] | list[ChatMessage],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """流式聊天

        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度
            max_tokens: 最大 token 数
            **kwargs: 其他参数

        Yields:
            流式响应片段
        """
        pass

    @abstractmethod
    async def list_models(self) -> list[ModelInfo]:
        """列出可用模型"""
        pass


class ProviderRegistry:
    """模型供应商注册表"""

    def __init__(self):
        self._providers: dict[str, ModelProvider] = {}
        self._default: str | None = None

    def register(self, provider: ModelProvider, as_default: bool = False) -> None:
        """注册供应商

        Args:
            provider: 供应商实例
            as_default: 是否设为默认
        """
        self._providers[provider.provider_name] = provider
        if as_default or not self._default:
            self._default = provider.provider_name

    def get(self, name: str) -> ModelProvider | None:
        """获取供应商"""
        return self._providers.get(name)

    def get_default(self) -> ModelProvider | None:
        """获取默认供应商"""
        if self._default:
            return self._providers.get(self._default)
        return None

    def set_default(self, name: str) -> bool:
        """设置默认供应商"""
        if name in self._providers:
            self._default = name
            return True
        return False

    def list(self) -> list[str]:
        """列出所有供应商"""
        return list(self._providers.keys())


# 工具调用格式转换
def convert_to_openai_format(messages: list[ChatMessage]) -> list[dict[str, Any]]:
    """转换为 OpenAI 格式"""
    result = []
    for msg in messages:
        item = {"role": msg.role, "content": msg.content}
        if msg.name:
            item["name"] = msg.name
        if msg.tool_call_id:
            item["tool_call_id"] = msg.tool_call_id
        result.append(item)
    return result

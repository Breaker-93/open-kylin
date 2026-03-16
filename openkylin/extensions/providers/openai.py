"""OpenAI 供应商 - OpenAI Provider"""

import os
from typing import Any, AsyncIterator

import aiohttp

from openkylin.extensions.providers.base import (
    ChatMessage, ModelProvider, ModelInfo, ProviderRegistry
)


class OpenAIProvider(ModelProvider):
    """OpenAI 模型供应商

    支持 GPT-4, GPT-4 Turbo, GPT-3.5 Turbo 等模型。
    """

    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        self._api_key = api_key or os.getenv("OPENAI_API_KEY")
        self._base_url = base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self._session: aiohttp.ClientSession | None = None

    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def default_model(self) -> str:
        return "gpt-4"

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def chat(
        self,
        messages: list[dict[str, Any]] | list[ChatMessage],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs
    ) -> str:
        """同步聊天"""
        # 转换消息格式
        if messages and isinstance(messages[0], ChatMessage):
            messages = [
                {"role": m.role, "content": m.content}
                for m in messages
            ]

        model = model or self.default_model

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }

        if max_tokens:
            payload["max_tokens"] = max_tokens

        # 添加工具调用支持
        if "tools" in kwargs:
            payload["tools"] = kwargs.pop("tools")

        payload.update(kwargs)

        session = await self._get_session()
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        async with session.post(
            f"{self._base_url}/chat/completions",
            json=payload,
            headers=headers
        ) as resp:
            if resp.status != 200:
                error = await resp.text()
                raise Exception(f"OpenAI API error: {error}")

            result = await resp.json()

            # 处理工具调用
            choice = result["choices"][0]
            if choice.get("finish_reason") == "tool_calls":
                # 有工具调用，返回调用信息
                tool_calls = choice["message"].get("tool_calls", [])
                return str(tool_calls)

            return choice["message"]["content"]

    async def stream_chat(
        self,
        messages: list[dict[str, Any]] | list[ChatMessage],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """流式聊天"""
        if messages and isinstance(messages[0], ChatMessage):
            messages = [
                {"role": m.role, "content": m.content}
                for m in messages
            ]

        model = model or self.default_model

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": True,
        }

        if max_tokens:
            payload["max_tokens"] = max_tokens
        payload.update(kwargs)

        session = await self._get_session()
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        async with session.post(
            f"{self._base_url}/chat/completions",
            json=payload,
            headers=headers
        ) as resp:
            if resp.status != 200:
                error = await resp.text()
                raise Exception(f"OpenAI API error: {error}")

            async for line in resp.content:
                line = line.decode("utf-8").strip()
                if not line or not line.startswith("data:"):
                    continue

                if line == "data: [DONE]":
                    break

                data = line[5:].strip()
                try:
                    import json
                    chunk = json.loads(data)
                    delta = chunk["choices"][0].get("delta", {})
                    if "content" in delta:
                        yield delta["content"]
                except Exception:
                    pass

    async def list_models(self) -> list[ModelInfo]:
        """列出可用模型"""
        session = await self._get_session()
        headers = {
            "Authorization": f"Bearer {self._api_key}",
        }

        async with session.get(
            f"{self._base_url}/models",
            headers=headers
        ) as resp:
            if resp.status != 200:
                return []

            result = await resp.json()
            models = []

            for m in result.get("data", []):
                models.append(ModelInfo(
                    id=m["id"],
                    name=m["id"],
                    provider="openai",
                    context_length=m.get("context_window", 4096),
                ))

            return models


class AzureOpenAIProvider(OpenAIProvider):
    """Azure OpenAI 供应商"""

    def __init__(self, api_key: str, endpoint: str, api_version: str = "2024-02-01"):
        super().__init__(api_key=api_key)
        self._endpoint = endpoint
        self._api_version = api_version
        self._base_url = f"{endpoint}/openai/deployments"

    @property
    def provider_name(self) -> str:
        return "azure-openai"

    async def chat(self, messages, model: str | None = None, **kwargs) -> str:
        """Azure OpenAI 聊天"""
        deployment = model or os.getenv("AZURE_DEPLOYMENT_NAME", "gpt-4")

        session = await self._get_session()
        headers = {
            "api-key": self._api_key,
            "Content-Type": "application/json",
        }

        url = f"{self._base_url}/{deployment}/chat/completions?api-version={self._api_version}"

        payload = {"messages": messages, "temperature": kwargs.get("temperature", 0.7)}
        if "max_tokens" in kwargs:
            payload["max_tokens"] = kwargs["max_tokens"]

        async with session.post(url, json=payload, headers=headers) as resp:
            if resp.status != 200:
                error = await resp.text()
                raise Exception(f"Azure OpenAI API error: {error}")

            result = await resp.json()
            return result["choices"][0]["message"]["content"]


# 注册默认供应商
def get_default_registry() -> ProviderRegistry:
    """获取默认供应商注册表"""
    registry = ProviderRegistry()

    # 添加 OpenAI
    openai = OpenAIProvider()
    registry.register(openai, as_default=True)

    return registry

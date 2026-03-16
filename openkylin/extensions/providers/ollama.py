"""Ollama 供应商 - Ollama Provider

支持本地运行的 Ollama 模型服务。
"""

import os
from typing import Any, AsyncIterator

import aiohttp

from openkylin.extensions.providers.base import (
    ChatMessage, ModelProvider, ModelInfo
)


class OllamaProvider(ModelProvider):
    """Ollama 本地模型供应商

    支持连接到本地或远程 Ollama 服务。
    """

    def __init__(self, base_url: str | None = None):
        self._base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self._session: aiohttp.ClientSession | None = None

    @property
    def provider_name(self) -> str:
        return "ollama"

    @property
    def default_model(self) -> str:
        return "llama2"

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
            "stream": False,
        }

        if max_tokens:
            payload["num_predict"] = max_tokens

        session = await self._get_session()

        async with session.post(
            f"{self._base_url}/api/chat",
            json=payload
        ) as resp:
            if resp.status != 200:
                error = await resp.text()
                raise Exception(f"Ollama API error: {error}")

            result = await resp.json()
            return result["message"]["content"]

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
            payload["num_predict"] = max_tokens

        session = await self._get_session()

        async with session.post(
            f"{self._base_url}/api/chat",
            json=payload
        ) as resp:
            if resp.status != 200:
                error = await resp.text()
                raise Exception(f"Ollama API error: {error}")

            async for line in resp.content:
                line = line.decode("utf-8").strip()
                if not line:
                    continue

                try:
                    import json
                    chunk = json.loads(line)
                    if "message" in chunk and "content" in chunk["message"]:
                        content = chunk["message"]["content"]
                        if content:
                            yield content
                except Exception:
                    pass

    async def list_models(self) -> list[ModelInfo]:
        """列出可用模型"""
        session = await self._get_session()

        try:
            async with session.get(f"{self._base_url}/api/tags") as resp:
                if resp.status != 200:
                    return []

                result = await resp.json()
                models = []

                for m in result.get("models", []):
                    models.append(ModelInfo(
                        id=m["name"],
                        name=m["name"],
                        provider="ollama",
                        context_length=m.get("context_window", 4096),
                    ))

                return models
        except Exception:
            return []

    async def pull_model(self, model: str, insecure: bool = False) -> AsyncIterator[dict]:
        """下载/更新模型

        Args:
            model: 模型名称
            insecure: 允许不安全连接

        Yields:
            下载进度
        """
        session = await self._get_session()

        payload = {"name": model, "insecure": insecure}

        async with session.post(
            f"{self._base_url}/api/pull",
            json=payload
        ) as resp:
            if resp.status != 200:
                error = await resp.text()
                raise Exception(f"Ollama pull error: {error}")

            async for line in resp.content:
                line = line.decode("utf-8").strip()
                if line:
                    try:
                        import json
                        yield json.loads(line)
                    except Exception:
                        pass

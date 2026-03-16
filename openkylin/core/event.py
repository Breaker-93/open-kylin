"""事件总线 - Event Bus

提供基于发布-订阅模式的事件系统，支持异步事件处理。
"""

import asyncio
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Awaitable, Callable, Protocol


class EventType(str, str):
    """事件类型常量"""
    MESSAGE_RECEIVED = "message.received"
    MESSAGE_SENT = "message.sent"
    TOOL_CALLED = "tool.called"
    TOOL_RESULT = "tool.result"
    AGENT_START = "agent.start"
    AGENT_END = "agent.end"
    AGENT_ERROR = "agent.error"
    PLUGIN_LOADED = "plugin.loaded"
    PLUGIN_UNLOADED = "plugin.unloaded"
    CHANNEL_CONNECTED = "channel.connected"
    CHANNEL_DISCONNECTED = "channel.disconnected"


@dataclass
class Event:
    """事件对象

    Attributes:
        type: 事件类型
        data: 事件数据
        timestamp: 事件时间
    """
    type: str
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


EventHandler = Callable[[Event], Awaitable[None]]


class EventBus:
    """事件总线 - 发布订阅模式实现

    Example:
        async def handle_message(event: Event):
            print(f"Received: {event.data}")

        bus = EventBus()
        bus.subscribe(EventType.MESSAGE_RECEIVED, handle_message)
        await bus.publish(Event(type=EventType.MESSAGE_RECEIVED, data={"text": "hello"}))
    """

    def __init__(self):
        self._handlers: dict[str, list[EventHandler]] = defaultdict(list)
        self._middlewares: list[Callable[[Event], Awaitable[Event | None]]] = []

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """订阅事件

        Args:
            event_type: 事件类型
            handler: 事件处理函数
        """
        self._handlers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        """取消订阅

        Args:
            event_type: 事件类型
            handler: 事件处理函数
        """
        if event_type in self._handlers:
            self._handlers[event_type].remove(handler)

    def use(self, middleware: Callable[[Event], Awaitable[Event | None]]) -> None:
        """添加中间件

        Args:
            middleware: 中间件函数，接收事件返回处理后的事件或None(拦截)
        """
        self._middlewares.append(middleware)

    async def publish(self, event: Event) -> None:
        """发布事件

        Args:
            event: 事件对象
        """
        # 执行中间件
        for middleware in self._middlewares:
            result = await middleware(event)
            if result is None:
                return  # 被中间件拦截
            event = result

        # 派发到处理器
        handlers = self._handlers.get(event.type, [])
        if not handlers:
            handlers = self._handlers.get("*", [])  # 通配符处理器

        # 并行执行所有处理器
        if handlers:
            await asyncio.gather(*[handler(event) for handler in handlers], return_exceptions=True)

    async def publish_sync(self, event: Event) -> list[Any]:
        """同步发布事件并收集结果

        Args:
            event: 事件对象

        Returns:
            所有处理器的返回值列表
        """
        handlers = self._handlers.get(event.type, [])
        if not handlers:
            handlers = self._handlers.get("*", [])

        results = []
        for handler in handlers:
            try:
                result = await handler(event)
                results.append(result)
            except Exception as e:
                results.append(e)

        return results

    def clear(self, event_type: str | None = None) -> None:
        """清除事件处理器

        Args:
            event_type: 要清除的事件类型，None表示清除所有
        """
        if event_type:
            self._handlers.pop(event_type, None)
        else:
            self._handlers.clear()
            self._middlewares.clear()

    def list_handlers(self) -> dict[str, int]:
        """列出所有事件处理器数量"""
        return {event_type: len(handlers) for event_type, handlers in self._handlers.items()}

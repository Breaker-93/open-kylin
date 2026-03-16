"""消息路由器 - Message Router

负责将消息路由到正确的处理程序和渠道。
"""

import asyncio
from dataclasses import dataclass, field
from typing import Any, Callable

from openkylin.core.message import Message
from openkylin.core.event import EventBus, EventType, Event


@dataclass
class Route:
    """路由规则"""
    channel: str           # 渠道标识
    pattern: str          # 消息匹配模式
    handler: Callable      # 处理函数
    priority: int = 0     # 优先级


class MessageRouter:
    """消息路由器

    Example:
        router = MessageRouter(event_bus)

        async def handle_dingtalk(message: Message):
            # 处理钉钉消息
            pass

        router.add_route("dingtalk", ".*", handle_dingtalk)
        await router.route(message)
    """

    def __init__(self, event_bus: EventBus | None = None):
        self._event_bus = event_bus or EventBus()
        self._routes: dict[str, list[Route]] = {}  # channel -> routes
        self._default_handler: Callable | None = None
        self._middlewares: list[Callable[[Message], bool]] = []

    def add_route(self, channel: str, pattern: str, handler: Callable, priority: int = 0) -> None:
        """添加路由规则

        Args:
            channel: 渠道标识
            pattern: 消息匹配模式（正则表达式）
            handler: 处理函数
            priority: 优先级
        """
        import re
        route = Route(channel=channel, pattern=pattern, handler=handler, priority=priority)
        route.regex = re.compile(pattern)

        if channel not in self._routes:
            self._routes[channel] = []
        self._routes[channel].append(route)

        # 按优先级排序
        self._routes[channel].sort(key=lambda r: r.priority, reverse=True)

    def set_default(self, handler: Callable) -> None:
        """设置默认处理器"""
        self._default_handler = handler

    def use(self, middleware: Callable[[Message], bool]) -> None:
        """添加中间件

        Args:
            middleware: 中间件函数，返回True继续，False拦截

        Returns:
            None
        """
        self._middlewares.append(middleware)

    async def route(self, message: Message) -> Any:
        """路由消息

        Args:
            message: 消息对象

        Returns:
            处理结果
        """
        # 执行中间件
        for middleware in self._middlewares:
            if not middleware(message):
                return None

        # 发布接收事件
        await self._event_bus.publish(Event(
            type=EventType.MESSAGE_RECEIVED,
            data={"message": message.to_dict()}
        ))

        # 查找匹配的路由
        channel_routes = self._routes.get(message.channel, [])
        for route in channel_routes:
            if route.regex.match(message.content):
                try:
                    result = route.handler(message)

                    # 支持异步处理
                    if asyncio.iscoroutine(result):
                        result = await result

                    await self._event_bus.publish(Event(
                        type=EventType.MESSAGE_SENT,
                        data={"message": message.to_dict(), "response": str(result) if result else None}
                    ))

                    return result
                except Exception as e:
                    # 路由处理出错
                    print(f"Route handler error: {e}")
                    continue

        # 使用默认处理器
        if self._default_handler:
            result = self._default_handler(message)
            if asyncio.iscoroutine(result):
                result = await result
            return result

        return None

    def remove_route(self, channel: str, pattern: str) -> bool:
        """移除路由规则"""
        if channel not in self._routes:
            return False

        self._routes[channel] = [
            r for r in self._routes[channel] if r.pattern != pattern
        ]
        return True

    def list_routes(self) -> dict[str, int]:
        """列出所有路由"""
        return {channel: len(routes) for channel, routes in self._routes.items()}


class RoundRobinRouter:
    """轮询路由器 - 支持多个 Agent 实例的负载均衡"""

    def __init__(self, agents: list, event_bus: EventBus | None = None):
        self._agents = agents
        self._event_bus = event_bus or EventBus()
        self._index = 0
        self._lock = asyncio.Lock()

    async def route(self, message: Message) -> Any:
        """轮询路由到下一个 Agent"""
        async with self._lock:
            agent = self._agents[self._index]
            self._index = (self._index + 1) % len(self._agents)

        return await agent.run(message)

    def add_agent(self, agent) -> None:
        """添加 Agent"""
        self._agents.append(agent)

    def remove_agent(self, name: str) -> bool:
        """移除 Agent"""
        for i, agent in enumerate(self._agents):
            if agent.name == name:
                self._agents.pop(i)
                return True
        return False

    def list_agents(self) -> list[str]:
        """列出所有 Agent"""
        return [agent.name for agent in self._agents]

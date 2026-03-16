"""Agent 引擎 - 基于 ReAct 模式的智能体实现

ReAct (Reason + Act) 模式：
- Thought: 思考当前状态和下一步行动
- Action: 执行工具或调用模型
- Observation: 观察结果
- Repeat until 完成
"""

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from openkylin.core.message import Message, Role
from openkylin.core.event import EventBus, EventType


class AgentState(str, Enum):
    """Agent 状态"""
    IDLE = "idle"
    THINKING = "thinking"
    ACTING = "acting"
    WAITING = "waiting"
    ERROR = "error"


@dataclass
class ToolCall:
    """工具调用"""
    name: str
    args: dict[str, Any]
    result: Any = None
    error: str | None = None


@dataclass
class AgentConfig:
    """Agent 配置"""
    name: str = "assistant"
    model: str = "gpt-4"
    temperature: float = 0.7
    max_steps: int = 10
    system_prompt: str = "You are a helpful AI assistant."
    tools: list[dict[str, Any]] = field(default_factory=list)


class Agent(ABC):
    """Agent 抽象基类"""

    @property
    @abstractmethod
    def name(self) -> str:
        """Agent 名称"""
        pass

    @abstractmethod
    async def run(self, message: Message) -> Message:
        """执行 Agent 处理

        Args:
            message: 用户消息

        Returns:
            Agent 响应消息
        """
        pass

    @abstractmethod
    async def think(self, prompt: str) -> str:
        """思考步骤 - 调用模型生成响应

        Args:
            prompt: 提示词

        Returns:
            模型响应
        """
        pass

    @abstractmethod
    async def act(self, tool_name: str, args: dict[str, Any]) -> Any:
        """执行工具

        Args:
            tool_name: 工具名称
            args: 工具参数

        Returns:
            工具执行结果
        """
        pass


class ReActAgent(Agent):
    """基于 ReAct 模式的 Agent 实现"""

    def __init__(
        self,
        config: AgentConfig,
        provider,  # ModelProvider
        tool_registry,
        event_bus: EventBus | None = None,
    ):
        self._config = config
        self._provider = provider
        self._tool_registry = tool_registry
        self._event_bus = event_bus or EventBus()
        self._state = AgentState.IDLE
        self._history: list[Message] = []

    @property
    def name(self) -> str:
        return self._config.name

    @property
    def state(self) -> AgentState:
        return self._state

    async def run(self, message: Message) -> Message:
        """执行 ReAct 循环"""
        # 添加用户消息到历史
        self._history.append(message)

        # 发布开始事件
        await self._event_bus.publish(Event(
            type=EventType.AGENT_START,
            data={"message": message.to_dict()}
        ))

        try:
            self._state = AgentState.THINKING
            response = await self._react_loop(message)

            assistant_msg = Message(
                role=Role.ASSISTANT,
                content=response,
                channel=message.channel,
            )
            self._history.append(assistant_msg)

            await self._event_bus.publish(Event(
                type=EventType.AGENT_END,
                data={"response": assistant_msg.to_dict()}
            ))

            return assistant_msg

        except Exception as e:
            self._state = AgentState.ERROR
            await self._event_bus.publish(Event(
                type=EventType.AGENT_ERROR,
                data={"error": str(e)}
            ))
            raise

        finally:
            self._state = AgentState.IDLE

    async def _react_loop(self, user_message: Message) -> str:
        """ReAct 循环"""
        max_steps = self._config.max_steps
        steps = 0
        final_response = ""

        # 构建消息列表
        messages = self._build_messages(user_message)

        while steps < max_steps:
            steps += 1

            # 1. Think - 调用模型
            self._state = AgentState.THINKING
            response = await self._provider.chat(messages)

            # 解析模型响应，判断是否需要调用工具
            tool_calls = self._parse_tool_calls(response)

            if not tool_calls:
                # 没有工具调用，返回最终响应
                final_response = response
                break

            # 2. Act - 执行工具
            for tool_call in tool_calls:
                self._state = AgentState.ACTING
                result = await self.act(tool_call.name, tool_call.args)
                tool_call.result = result

                # 将工具结果添加到消息历史
                messages.append({
                    "role": "assistant",
                    "content": response
                })
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.name,
                    "content": str(result)
                })

                await self._event_bus.publish(Event(
                    type=EventType.TOOL_RESULT,
                    data={"tool": tool_call.name, "result": str(result)}
                ))

            # 3. 继续循环，让模型根据工具结果生成下一步响应

        return final_response

    async def think(self, prompt: str) -> str:
        """直接调用模型思考"""
        messages = [{"role": "system", "content": self._config.system_prompt}]
        messages.append({"role": "user", "content": prompt})
        return await self._provider.chat(messages)

    async def act(self, tool_name: str, args: dict[str, Any]) -> Any:
        """执行工具"""
        await self._event_bus.publish(Event(
            type=EventType.TOOL_CALLED,
            data={"tool": tool_name, "args": args}
        ))

        tool = self._tool_registry.get(tool_name)
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found")

        result = await tool.execute(**args)
        return result

    def _build_messages(self, user_message: Message) -> list[dict[str, Any]]:
        """构建消息列表"""
        messages = [{"role": "system", "content": self._config.system_prompt}]

        # 添加历史消息
        for msg in self._history[-10:]:  # 保留最近10条
            role = msg.role.value if isinstance(msg.role, Role) else msg.role
            messages.append({"role": role, "content": msg.content})

        # 添加当前用户消息
        messages.append({
            "role": "user",
            "content": user_message.content
        })

        return messages

    def _parse_tool_calls(self, response: str) -> list[ToolCall]:
        """解析模型响应中的工具调用

        简单实现：解析 JSON 格式的工具调用
        实际生产环境应使用模型原生的 tool calling 功能
        """
        import json
        tool_calls = []

        try:
            # 尝试解析 JSON 格式
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
                data = json.loads(json_str)
                if isinstance(data, list):
                    for item in data:
                        if "name" in item:
                            tool_calls.append(ToolCall(
                                name=item["name"],
                                args=item.get("arguments", {})
                            ))
        except Exception:
            pass

        return tool_calls

    def get_history(self) -> list[Message]:
        """获取对话历史"""
        return self._history.copy()

    def clear_history(self) -> None:
        """清空对话历史"""
        self._history.clear()

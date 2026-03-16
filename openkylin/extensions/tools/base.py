"""工具基类 - Tool Base Classes"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from openkylin.core.plugin import Plugin, PluginMetadata, PluginType


@dataclass
class ToolDefinition:
    """工具定义 - 用于暴露给 AI 模型"""
    name: str
    description: str
    parameters: dict[str, Any] = field(default_factory=dict)
    # OpenAI function calling 格式
    function: dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolResult:
    """工具执行结果"""
    success: bool
    result: Any = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "result": self.result,
            "error": self.error,
            "metadata": self.metadata,
        }


class Tool(ABC, Plugin):
    """工具抽象基类

    所有工具插件必须继承此类并实现 execute 方法。
    """

    def __init__(self):
        self._definition: ToolDefinition | None = None

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name=self.name,
            plugin_type=PluginType.TOOL,
            description=self.description,
        )

    @property
    @abstractmethod
    def name(self) -> str:
        """工具名称"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """工具描述"""
        pass

    @property
    def definition(self) -> ToolDefinition:
        """获取工具定义（用于 AI 模型）"""
        if self._definition is None:
            self._definition = ToolDefinition(
                name=self.name,
                description=self.description,
                parameters=self.get_parameters(),
                function=self.to_function_call(),
            )
        return self._definition

    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """执行工具

        Args:
            **kwargs: 工具参数

        Returns:
            ToolResult: 执行结果
        """
        pass

    def get_parameters(self) -> dict[str, Any]:
        """获取参数定义

        Returns:
            JSON Schema 格式的参数定义
        """
        return {
            "type": "object",
            "properties": {},
            "required": [],
        }

    def to_function_call(self) -> dict[str, Any]:
        """转换为 OpenAI function calling 格式"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.get_parameters(),
        }

    async def initialize(self, config: dict[str, Any]) -> None:
        """初始化工具"""
        pass

    async def shutdown(self) -> None:
        """关闭工具"""
        pass


class CompositeTool(Tool):
    """组合工具 - 将多个工具组合在一起"""

    def __init__(self, name: str, description: str, tools: list[Tool]):
        super().__init__()
        self._name = name
        self._description = description
        self._tools = {tool.name: tool for tool in tools}

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def tools(self) -> dict[str, Tool]:
        return self._tools.copy()

    async def execute(self, tool_name: str = None, **kwargs) -> ToolResult:
        """执行指定的子工具"""
        if tool_name is None:
            return ToolResult(success=False, error="tool_name required")

        tool = self._tools.get(tool_name)
        if not tool:
            return ToolResult(success=False, error=f"Tool '{tool_name}' not found")

        result = await tool.execute(**kwargs)
        return result

    def add_tool(self, tool: Tool) -> None:
        """添加子工具"""
        self._tools[tool.name] = tool
        self._definition = None  # 重置定义缓存

    def remove_tool(self, name: str) -> bool:
        """移除子工具"""
        if name in self._tools:
            del self._tools[name]
            self._definition = None
            return True
        return False


class BuiltinTool(Tool):
    """内置工具基类

    提供常用工具的基础实现。
    """

    pass

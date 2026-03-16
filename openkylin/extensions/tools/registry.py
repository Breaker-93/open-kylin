"""工具注册表 - Tool Registry

管理所有可用工具的注册和调用。
"""

from typing import Any

from openkylin.extensions.tools.base import Tool, ToolDefinition, ToolResult


class ToolRegistry:
    """工具注册表

    Example:
        registry = ToolRegistry()

        # 注册工具
        registry.register(MyTool())

        # 获取工具
        tool = registry.get("my_tool")

        # 列出所有工具
        tools = registry.list()

        # 执行工具
        result = await registry.execute("my_tool", arg1="value")
    """

    def __init__(self):
        self._tools: dict[str, Tool] = {}
        self._definitions: dict[str, ToolDefinition] = {}

    def register(self, tool: Tool) -> None:
        """注册工具

        Args:
            tool: 工具实例
        """
        self._tools[tool.name] = tool
        self._definitions[tool.name] = tool.definition

    def unregister(self, name: str) -> bool:
        """注销工具

        Args:
            name: 工具名称

        Returns:
            是否成功
        """
        if name in self._tools:
            del self._tools[name]
            del self._definitions[name]
            return True
        return False

    def get(self, name: str) -> Tool | None:
        """获取工具

        Args:
            name: 工具名称

        Returns:
            工具实例或None
        """
        return self._tools.get(name)

    def get_definition(self, name: str) -> ToolDefinition | None:
        """获取工具定义

        Args:
            name: 工具名称

        Returns:
            工具定义或None
        """
        return self._definitions.get(name)

    def list(self) -> list[str]:
        """列出所有工具名称

        Returns:
            工具名称列表
        """
        return list(self._tools.keys())

    def list_definitions(self) -> list[ToolDefinition]:
        """列出所有工具定义

        Returns:
            工具定义列表（用于 AI 模型）
        """
        return list(self._definitions.values())

    async def execute(self, name: str, **kwargs) -> ToolResult:
        """执行工具

        Args:
            name: 工具名称
            **kwargs: 工具参数

        Returns:
            执行结果
        """
        tool = self._tools.get(name)
        if not tool:
            return ToolResult(
                success=False,
                error=f"Tool '{name}' not found"
            )

        try:
            result = await tool.execute(**kwargs)
            if not isinstance(result, ToolResult):
                result = ToolResult(success=True, result=result)
            return result
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e)
            )

    async def execute_many(self, calls: list[dict[str, Any]]) -> list[ToolResult]:
        """批量执行工具

        Args:
            calls: 工具调用列表 [{"name": "tool1", "args": {...}}, ...]

        Returns:
            结果列表
        """
        import asyncio
        tasks = [
            self.execute(call["name"], **call.get("args", {}))
            for call in calls
        ]
        return await asyncio.gather(*tasks)

    def has(self, name: str) -> bool:
        """检查工具是否存在"""
        return name in self._tools

    def clear(self) -> None:
        """清空所有工具"""
        self._tools.clear()
        self._definitions.clear()

    def __len__(self) -> int:
        return len(self._tools)

    def __contains__(self, name: str) -> bool:
        return name in self._tools


class ToolCatalog:
    """工具目录 - 预定义的内置工具集"""

    @staticmethod
    def get_builtin_tools() -> list[type[Tool]]:
        """获取内置工具列表

        Returns:
            工具类列表
        """
        from openkylin.extensions.tools import builtin
        return builtin.get_builtin_tools()

    @staticmethod
    def create_default_registry() -> ToolRegistry:
        """创建默认工具注册表（包含内置工具）"""
        registry = ToolRegistry()

        for tool_class in ToolCatalog.get_builtin_tools():
            tool = tool_class()
            registry.register(tool)

        return registry


# 延迟导入内置工具
import sys
from importlib import import_module as _import

def _ensure_builtin_loaded():
    """确保内置工具模块已加载"""
    if "openkylin.extensions.tools.builtin" not in sys.modules:
        try:
            _import("openkylin.extensions.tools.builtin")
        except ImportError:
            pass  # 模块不存在，跳过

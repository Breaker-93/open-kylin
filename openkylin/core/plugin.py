"""插件管理系统 - Plugin Management System

基于 entry_points 的动态插件加载机制。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from importlib import import_module
from importlib.metadata import entry_points
from pathlib import Path
from typing import Any, Callable, Type


class PluginType(str, Enum):
    """插件类型"""
    CHANNEL = "channel"      # 消息渠道
    TOOL = "tool"           # 工具插件
    PROVIDER = "provider"   # 模型供应商
    MEMORY = "memory"       # 记忆存储


@dataclass
class PluginMetadata:
    """插件元数据"""
    name: str
    version: str = "1.0.0"
    description: str = ""
    author: str = ""
    plugin_type: PluginType = PluginType.TOOL
    enabled: bool = True
    config: dict[str, Any] = field(default_factory=dict)


class Plugin(ABC):
    """插件基类"""

    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """插件元数据"""
        pass

    @abstractmethod
    async def initialize(self, config: dict[str, Any]) -> None:
        """初始化插件

        Args:
            config: 插件配置
        """
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        """关闭插件"""
        pass


class PluginRegistry:
    """插件注册表 - 管理所有已加载的插件"""

    def __init__(self):
        self._plugins: dict[str, Plugin] = {}
        self._factories: dict[str, Type[Plugin]] = {}
        self._configs: dict[str, dict[str, Any]] = {}

    def register(self, name: str, factory: Type[Plugin], config: dict[str, Any] | None = None) -> None:
        """注册插件工厂

        Args:
            name: 插件名称
            factory: 插件类
            config: 插件配置
        """
        self._factories[name] = factory
        self._configs[name] = config or {}

    async def load(self, name: str) -> Plugin:
        """加载插件

        Args:
            name: 插件名称

        Returns:
            插件实例
        """
        if name in self._plugins:
            return self._plugins[name]

        if name not in self._factories:
            raise ValueError(f"Plugin '{name}' not found in registry")

        factory = self._factories[name]
        plugin = factory()
        await plugin.initialize(self._configs.get(name, {}))
        self._plugins[name] = plugin
        return plugin

    async def unload(self, name: str) -> None:
        """卸载插件

        Args:
            name: 插件名称
        """
        if name in self._plugins:
            plugin = self._plugins[name]
            await plugin.shutdown()
            del self._plugins[name]

    def get(self, name: str) -> Plugin | None:
        """获取已加载的插件

        Args:
            name: 插件名称

        Returns:
            插件实例或None
        """
        return self._plugins.get(name)

    def list(self, plugin_type: PluginType | None = None) -> list[str]:
        """列出已注册的插件

        Args:
            plugin_type: 插件类型过滤

        Returns:
            插件名称列表
        """
        names = list(self._factories.keys())
        if plugin_type:
            names = [
                name for name, factory in self._factories.items()
                if hasattr(factory, 'metadata') and
                factory.metadata.plugin_type == plugin_type
            ]
        return names

    def loaded(self) -> list[str]:
        """返回已加载的插件名称"""
        return list(self._plugins.keys())


class PluginLoader:
    """插件加载器 - 从多种来源加载插件"""

    def __init__(self, registry: PluginRegistry):
        self._registry = registry
        self._discovered: dict[str, str] = {}  # name -> source

    def discover_from_entry_points(self, group: str = "openkylin.plugins") -> list[str]:
        """从 entry_points 发现插件

        Args:
            group: 插件组名

        Returns:
            发现的插件名称列表
        """
        discovered = []
        try:
            eps = entry_points(group=group)
            for ep in eps:
                name = ep.name
                self._discovered[name] = f"entry_point:{group}"
                discovered.append(name)
        except TypeError:
            # Python < 3.10 兼容
            for ep in entry_points().get(group, []):
                name = ep.name
                self._discovered[name] = f"entry_point:{group}"
                discovered.append(name)

        return discovered

    def discover_from_directory(self, directory: Path) -> list[str]:
        """从目录发现插件

        Args:
            directory: 插件目录

        Returns:
            发现的插件名称列表
        """
        discovered = []
        if not directory.exists():
            return discovered

        for path in directory.iterdir():
            if path.is_file() and path.suffix == ".py" and not path.name.startswith("_"):
                name = path.stem
                self._discovered[name] = str(path)
                discovered.append(name)
            elif path.is_dir() and (path / "__init__.py").exists():
                name = path.name
                self._discovered[name] = str(path)
                discovered.append(name)

        return discovered

    async def load_discovered(self) -> None:
        """加载所有已发现的插件"""
        for name, source in self._discovered.items():
            try:
                if source.startswith("entry_point:"):
                    eps = entry_points(group=source.split(":")[1])
                    ep = next((e for e in eps if e.name == name), None)
                    if ep:
                        plugin_class = ep.load()
                        self._registry.register(name, plugin_class)
                else:
                    # 从文件/目录加载
                    module = import_module(f"plugins.{name}")
                    if hasattr(module, "Plugin"):
                        self._registry.register(name, module.Plugin)
            except Exception as e:
                print(f"Failed to load plugin '{name}': {e}")

    def get_source(self, name: str) -> str | None:
        """获取插件来源"""
        return self._discovered.get(name)

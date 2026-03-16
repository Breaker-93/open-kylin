"""DAG 编排 - Directed Acyclic Graph

基于有向无环图的任务编排引擎。
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Awaitable


class NodeStatus(str, Enum):
    """节点状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class DAGNode:
    """DAG 节点

    Attributes:
        id: 节点 ID
        name: 节点名称
        handler: 处理函数
        dependencies: 依赖节点 ID 列表
        config: 节点配置
    """
    id: str
    name: str
    handler: Callable[[dict[str, Any]], Awaitable[dict[str, Any]]] | None = None
    dependencies: list[str] = field(default_factory=list)
    config: dict[str, Any] = field(default_factory=dict)
    status: NodeStatus = NodeStatus.PENDING
    result: dict[str, Any] | None = None
    error: str | None = None


class DAG:
    """有向无环图

    Example:
        dag = DAG()

        # 添加节点
        dag.add_node("step1", "获取数据", dependencies=[])
        dag.add_node("step2", "处理数据", dependencies=["step1"])
        dag.add_node("step3", "保存结果", dependencies=["step2"])

        # 执行
        results = await dag.execute({})
    """

    def __init__(self):
        self._nodes: dict[str, DAGNode] = {}

    def add_node(
        self,
        node_id: str,
        name: str,
        handler: Callable[[dict[str, Any]], Awaitable[dict[str, Any]]] | None = None,
        dependencies: list[str] | None = None,
        config: dict[str, Any] | None = None,
    ) -> None:
        """添加节点

        Args:
            node_id: 节点 ID
            name: 节点名称
            handler: 处理函数
            dependencies: 依赖节点
            config: 配置
        """
        node = DAGNode(
            id=node_id,
            name=name,
            handler=handler,
            dependencies=dependencies or [],
            config=config or {},
        )
        self._nodes[node_id] = node

    def remove_node(self, node_id: str) -> bool:
        """移除节点"""
        if node_id in self._nodes:
            del self._nodes[node_id]
            # 移除对该节点的依赖
            for node in self._nodes.values():
                if node_id in node.dependencies:
                    node.dependencies.remove(node_id)
            return True
        return False

    def get_node(self, node_id: str) -> DAGNode | None:
        """获取节点"""
        return self._nodes.get(node_id)

    def get_execution_order(self) -> list[list[str]]:
        """获取执行顺序（拓扑排序）

        Returns:
            分层执行顺序，每层内的节点可以并行执行
        """
        # 计算入度
        in_degree = {node_id: 0 for node_id in self._nodes}
        for node in self._nodes.values():
            for dep in node.dependencies:
                if dep in in_degree:
                    in_degree[dep] = in_degree.get(dep, 0)

        # 重新计算：每个节点的依赖入度
        in_degree = {node_id: 0 for node_id in self._nodes}
        for node in self._nodes.values():
            for dep in node.dependencies:
                in_degree[node_id] = in_degree.get(node_id, 0) + 1

        # 正确的入度计算
        in_degree = {node_id: 0 for node_id in self._nodes}
        for node in self._nodes.values():
            in_degree[node.id] = len(node.dependencies)

        # 拓扑排序（Kahn 算法）
        layers = []
        remaining = set(self._nodes.keys())

        while remaining:
            # 找出入度为 0 的节点
            ready = [n for n in remaining if in_degree[n] == 0]

            if not ready:
                raise ValueError("Cycle detected in DAG")

            layers.append(ready)

            # 移除这些节点
            for node_id in ready:
                remaining.remove(node_id)
                # 更新依赖该节点的入度
                for node in self._nodes.values():
                    if node_id in node.dependencies:
                        in_degree[node.id] -= 1

        return layers

    def validate(self) -> tuple[bool, str]:
        """验证 DAG 是否有环

        Returns:
            (是否有效, 错误信息)
        """
        try:
            self.get_execution_order()
            return True, ""
        except ValueError as e:
            return False, str(e)

    def list_nodes(self) -> list[DAGNode]:
        """列出所有节点"""
        return list(self._nodes.values())

    def __len__(self) -> int:
        return len(self._nodes)

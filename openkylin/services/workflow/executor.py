"""工作流执行器 - Workflow Executor"""

import asyncio
from dataclasses import dataclass, field
from typing import Any

from openkylin.services.workflow.dag import DAG, DAGNode, NodeStatus


@dataclass
class WorkflowResult:
    """工作流执行结果"""
    success: bool
    results: dict[str, Any] = field(default_factory=dict)
    errors: dict[str, str] = field(default_factory=dict)


class WorkflowExecutor:
    """工作流执行器

    执行 DAG 定义的工作流。
    """

    def __init__(self, dag: DAG, max_concurrency: int = 3):
        """
        Args:
            dag: DAG 实例
            max_concurrency: 最大并发数
        """
        self._dag = dag
        self._max_concurrency = max_concurrency

    async def execute(self, initial_input: dict[str, Any]) -> WorkflowResult:
        """执行工作流

        Args:
            initial_input: 初始输入

        Returns:
            执行结果
        """
        # 验证 DAG
        valid, error = self._dag.validate()
        if not valid:
            return WorkflowResult(
                success=False,
                errors={"validation": error}
            )

        # 获取执行顺序
        layers = self._dag.get_execution_order()

        # 收集所有结果
        all_results: dict[str, Any] = {"input": initial_input}

        # 逐层执行
        for layer in layers:
            # 准备当前层的输入
            layer_inputs = {}
            for node_id in layer:
                node = self._dag.get_node(node_id)
                if not node:
                    continue

                # 合并依赖节点的结果
                input_data = {**initial_input}
                for dep_id in node.dependencies:
                    if dep_id in all_results:
                        input_data[f"dep_{dep_id}"] = all_results[dep_id]

                layer_inputs[node_id] = input_data

            # 并行执行当前层
            layer_tasks = []
            for node_id, input_data in layer_inputs.items():
                task = self._execute_node(node_id, input_data, all_results)
                layer_tasks.append(task)

            layer_results = await asyncio.gather(*layer_tasks, return_exceptions=True)

            # 处理结果
            for node_id, result in zip(layer, layer_results):
                if isinstance(result, Exception):
                    node = self._dag.get_node(node_id)
                    if node:
                        node.status = NodeStatus.FAILED
                        node.error = str(result)
                    all_results[node_id] = None
                else:
                    all_results[node_id] = result

        # 检查是否有失败
        errors = {}
        for node in self._dag.list_nodes():
            if node.status == NodeStatus.FAILED:
                errors[node.id] = node.error or "Unknown error"

        return WorkflowResult(
            success=len(errors) == 0,
            results=all_results,
            errors=errors,
        )

    async def _execute_node(
        self,
        node_id: str,
        input_data: dict[str, Any],
        previous_results: dict[str, Any],
    ) -> Any:
        """执行单个节点"""
        node = self._dag.get_node(node_id)
        if not node:
            return None

        node.status = NodeStatus.RUNNING

        try:
            # 如果没有 handler，透传输入
            if node.handler:
                result = await node.handler(input_data)
            else:
                result = input_data

            node.status = NodeStatus.COMPLETED
            node.result = result

            return result

        except Exception as e:
            node.status = NodeStatus.FAILED
            node.error = str(e)
            raise


class SimpleWorkflowBuilder:
    """简单工作流构建器

    提供链式 API 构建工作流。
    """

    def __init__(self):
        self._dag = DAG()
        self._node_counter = 0

    def add_step(
        self,
        name: str,
        handler: Any = None,
        dependencies: list[str] | None = None,
    ) -> "SimpleWorkflowBuilder":
        """添加步骤"""
        import uuid
        node_id = f"step_{uuid.uuid4().hex[:8]}"
        self._dag.add_node(
            node_id=node_id,
            name=name,
            handler=handler,
            dependencies=dependencies or [],
        )
        return self

    def then(self, name: str, handler: Any = None) -> "SimpleWorkflowBuilder":
        """链式添加步骤（依赖上一步）"""
        # 获取最后添加的节点
        nodes = self._dag.list_nodes()
        deps = [nodes[-1].id] if nodes else []
        return self.add_step(name, handler, deps)

    def build(self) -> DAG:
        """构建 DAG"""
        return self._dag


# 便捷函数
def create_linear_workflow(steps: list[tuple[str, Any]]) -> DAG:
    """创建线性工作流

    Args:
        steps: [(名称, 处理函数), ...]

    Returns:
        DAG 实例
    """
    builder = SimpleWorkflowBuilder()

    for i, (name, handler) in enumerate(steps):
        deps = [f"step_{i-1}"] if i > 0 else []
        builder.add_step(name, handler, deps)

    return builder.build()

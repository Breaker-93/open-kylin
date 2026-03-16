"""检索器 - Retriever

RAG 系统的检索组件。
"""

from dataclasses import dataclass, field
from typing import Any

from openkylin.services.rag.vector_store import VectorStore, Document, SearchResult


@dataclass
class RetrievedContext:
    """检索到的上下文"""
    content: str
    source: str
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)


class Retriever:
    """检索器

    负责从向量存储中检索相关文档。
    """

    def __init__(self, vector_store: VectorStore):
        self._vector_store = vector_store
        self._default_top_k = 5

    async def retrieve(
        self,
        query: str,
        top_k: int | None = None,
        filter: dict[str, Any] | None = None,
    ) -> list[RetrievedContext]:
        """检索相关文档

        Args:
            query: 查询文本
            top_k: 返回数量
            filter: 过滤条件

        Returns:
            检索到的上下文列表
        """
        top_k = top_k or self._default_top_k

        results = await self._vector_store.search(
            query=query,
            limit=top_k,
            filter=filter,
        )

        contexts = []
        for result in results:
            contexts.append(RetrievedContext(
                content=result.document.content,
                source=result.document.id,
                score=result.score,
                metadata=result.document.metadata,
            ))

        return contexts

    async def retrieve_with_rerank(
        self,
        query: str,
        top_k: int = 10,
        final_k: int = 3,
    ) -> list[RetrievedContext]:
        """检索并重排序

        Args:
            query: 查询文本
            top_k: 初步检索数量
            final_k: 最终返回数量

        Returns:
            重排序后的上下文
        """
        # 初步检索
        contexts = await self.retrieve(query, top_k=top_k)

        # 简单重排序：基于关键词匹配
        query_keywords = set(query.lower().split())
        for ctx in contexts:
            ctx_keywords = set(ctx.content.lower().split())
            overlap = len(query_keywords & ctx_keywords)
            ctx.metadata["rerank_score"] = overlap

        # 排序并返回 top_k
        contexts.sort(key=lambda x: x.metadata.get("rerank_score", 0), reverse=True)
        return contexts[:final_k]

    def format_context(self, contexts: list[RetrievedContext]) -> str:
        """格式化检索到的上下文"""
        if not contexts:
            return ""

        formatted = "相关上下文：\n\n"
        for i, ctx in enumerate(contexts, 1):
            formatted += f"--- 来源 {i} (相关性: {ctx.score:.2f}) ---\n"
            formatted += f"{ctx.content}\n\n"

        return formatted


class RAG:
    """RAG 引擎

    完整的检索增强生成组件。
    """

    def __init__(
        self,
        vector_store: VectorStore,
        retriever: Retriever | None = None,
    ):
        self._vector_store = vector_store
        self._retriever = retriever or Retriever(vector_store)

    async def add_documents(self, documents: list[Document]) -> list[str]:
        """添加文档"""
        return await self._vector_store.add(documents)

    async def query(
        self,
        query: str,
        top_k: int = 5,
    ) -> str:
        """查询

        Args:
            query: 查询文本
            top_k: 返回数量

        Returns:
            格式化的检索结果
        """
        contexts = await self._retriever.retrieve(query, top_k=top_k)
        return self._retriever.format_context(contexts)

    async def query_with_sources(
        self,
        query: str,
        top_k: int = 5,
    ) -> tuple[str, list[RetrievedContext]]:
        """查询（带来源）"""
        contexts = await self._retriever.retrieve(query, top_k=top_k)
        formatted = self._retriever.format_context(contexts)
        return formatted, contexts

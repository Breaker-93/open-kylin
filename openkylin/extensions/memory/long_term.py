"""长期记忆 - Long Term Memory

基于向量存储的持久化记忆。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class MemoryEntry:
    """记忆条目"""
    id: str
    content: str
    embedding: list[float] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    access_count: int = 0


class LongTermMemory:
    """长期记忆 - 向量存储

    支持语义搜索的持久化记忆系统。
    需要配合向量数据库使用（如 Chroma、Qdrant）。
    """

    def __init__(self, collection_name: str = "long_term_memory", embedding_dim: int = 1536):
        """
        Args:
            collection_name: 集合名称
            embedding_dim: 向量维度
        """
        self._collection_name = collection_name
        self._embedding_dim = embedding_dim
        self._vector_store = None  # 延迟初始化
        self._entries: dict[str, MemoryEntry] = {}

    async def initialize(self, vector_store_backend: str = "memory") -> None:
        """初始化向量存储后端

        Args:
            vector_store_backend: 后端类型 (memory/chroma/qdrant)
        """
        if vector_store_backend == "chroma":
            try:
                import chromadb
                client = chromadb.Client()
                self._vector_store = client.get_or_create_collection(
                    self._collection_name
                )
            except ImportError:
                print("Chroma not installed, using in-memory storage")

        # 默认使用内存存储
        if self._vector_store is None:
            self._vector_store = {}

    async def add(self, content: str, metadata: dict[str, Any] | None = None) -> str:
        """添加记忆

        Args:
            content: 记忆内容
            metadata: 元数据

        Returns:
            记忆 ID
        """
        import uuid
        entry_id = str(uuid.uuid4())

        entry = MemoryEntry(
            id=entry_id,
            content=content,
            metadata=metadata or {},
        )

        self._entries[entry_id] = entry

        # 如果有向量存储后端，添加到向量索引
        if self._vector_store and hasattr(self._vector_store, 'add'):
            embedding = await self._get_embedding(content)
            if embedding:
                self._vector_store.add(
                    ids=[entry_id],
                    embeddings=[embedding],
                    documents=[content],
                    metadatas=[metadata or {}]
                )

        return entry_id

    async def search(self, query: str, limit: int = 5) -> list[MemoryEntry]:
        """语义搜索

        Args:
            query: 查询内容
            limit: 返回数量

        Returns:
            记忆条目列表
        """
        # 如果有向量存储后端，使用向量搜索
        if self._vector_store and hasattr(self._vector_store, 'query'):
            embedding = await self._get_embedding(query)
            if embedding:
                results = self._vector_store.query(
                    query_embeddings=[embedding],
                    n_results=limit
                )
                ids = results.get("ids", [[]])[0]
                return [self._entries[id] for id in ids if id in self._entries]

        # 回退：简单关键词匹配
        results = []
        query_lower = query.lower()
        for entry in self._entries.values():
            if query_lower in entry.content.lower():
                results.append(entry)
                if len(results) >= limit:
                    break

        # 更新访问计数
        for entry in results:
            entry.access_count += 1

        return results

    async def get(self, entry_id: str) -> MemoryEntry | None:
        """获取记忆"""
        entry = self._entries.get(entry_id)
        if entry:
            entry.access_count += 1
        return entry

    async def delete(self, entry_id: str) -> bool:
        """删除记忆"""
        if entry_id in self._entries:
            del self._entries[entry_id]
            if self._vector_store and hasattr(self._vector_store, 'delete'):
                self._vector_store.delete(ids=[entry_id])
            return True
        return False

    async def get_recent(self, limit: int = 10) -> list[MemoryEntry]:
        """获取最近记忆"""
        entries = sorted(
            self._entries.values(),
            key=lambda e: e.created_at,
            reverse=True
        )
        return entries[:limit]

    async def get_frequent(self, limit: int = 10) -> list[MemoryEntry]:
        """获取最常访问的记忆"""
        entries = sorted(
            self._entries.values(),
            key=lambda e: e.access_count,
            reverse=True
        )
        return entries[:limit]

    async def _get_embedding(self, text: str) -> list[float] | None:
        """获取文本嵌入

        简化实现，实际应调用嵌入模型
        """
        # TODO: 实现真实的嵌入生成
        # 可使用 OpenAI text-embedding-ada-002 或其他嵌入模型
        return None

    async def clear(self) -> None:
        """清空所有记忆"""
        self._entries.clear()
        if self._vector_store and hasattr(self._vector_store, 'delete'):
            self._vector_store.delete(where={})

    def count(self) -> int:
        """记忆数量"""
        return len(self._entries)

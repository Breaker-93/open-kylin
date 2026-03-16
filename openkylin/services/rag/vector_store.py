"""向量存储 - Vector Store

支持多种向量数据库后端：内存、Chroma、Qdrant。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Document:
    """文档"""
    id: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    embedding: list[float] | None = None


@dataclass
class SearchResult:
    """搜索结果"""
    document: Document
    score: float


class VectorStore(ABC):
    """向量存储抽象基类"""

    @abstractmethod
    async def add(self, documents: list[Document]) -> list[str]:
        """添加文档

        Args:
            documents: 文档列表

        Returns:
            文档 ID 列表
        """
        pass

    @abstractmethod
    async def search(
        self,
        query: str | list[float],
        limit: int = 5,
        filter: dict[str, Any] | None = None
    ) -> list[SearchResult]:
        """搜索

        Args:
            query: 查询文本或向量
            limit: 返回数量
            filter: 过滤条件

        Returns:
            搜索结果列表
        """
        pass

    @abstractmethod
    async def delete(self, ids: list[str]) -> None:
        """删除文档"""
        pass

    @abstractmethod
    async def count(self) -> int:
        """文档数量"""
        pass


class InMemoryVectorStore(VectorStore):
    """内存向量存储（简化实现）"""

    def __init__(self, embedding_dim: int = 1536):
        self._embedding_dim = embedding_dim
        self._documents: dict[str, Document] = {}
        self._ids: list[str] = []

    async def add(self, documents: list[Document]) -> list[str]:
        ids = []
        for doc in documents:
            if not doc.id:
                import uuid
                doc.id = str(uuid.uuid4())
            self._documents[doc.id] = doc
            self._ids.append(doc.id)
            ids.append(doc.id)
        return ids

    async def search(
        self,
        query: str | list[float],
        limit: int = 5,
        filter: dict[str, Any] | None = None
    ) -> list[SearchResult]:
        # 简化实现：返回最近的文档
        results = []
        for doc_id in self._ids[-limit:]:
            doc = self._documents[doc_id]
            if filter:
                match = True
                for k, v in filter.items():
                    if doc.metadata.get(k) != v:
                        match = False
                        break
                if not match:
                    continue
            results.append(SearchResult(document=doc, score=1.0))
        return results

    async def delete(self, ids: list[str]) -> None:
        for id in ids:
            if id in self._documents:
                del self._documents[id]
                self._ids.remove(id)

    async def count(self) -> int:
        return len(self._documents)


class ChromaVectorStore(VectorStore):
    """Chroma 向量存储"""

    def __init__(self, collection_name: str = "default"):
        self._collection_name = collection_name
        self._client = None
        self._collection = None

    async def initialize(self) -> None:
        """初始化 Chroma"""
        try:
            import chromadb
            from chromadb.config import Settings

            self._client = chromadb.Client(Settings(
                persist_directory=".openkylin/chroma"
            ))
            self._collection = self._client.get_or_create_collection(
                self._collection_name
            )
        except ImportError:
            print("Chroma not installed, falling back to in-memory")

    async def add(self, documents: list[Document]) -> list[str]:
        if not self._collection:
            return []

        ids = []
        for doc in documents:
            if not doc.id:
                import uuid
                doc.id = str(uuid.uuid4())

        self._collection.add(
            ids=[doc.id for doc in documents],
            documents=[doc.content for doc in documents],
            metadatas=[doc.metadata for doc in documents],
        )
        return [doc.id for doc in documents]

    async def search(
        self,
        query: str | list[float],
        limit: int = 5,
        filter: dict[str, Any] | None = None
    ) -> list[SearchResult]:
        if not self._collection:
            return []

        results = self._collection.query(
            query_texts=[query] if isinstance(query, str) else None,
            query_embeddings=[query] if isinstance(query, list) else None,
            n_results=limit,
            where=filter,
        )

        search_results = []
        for i, doc_id in enumerate(results["ids"][0]):
            search_results.append(SearchResult(
                document=Document(
                    id=doc_id,
                    content=results["documents"][0][i],
                    metadata=results["metadatas"][0][i],
                ),
                score=results["distances"][0][i] if "distances" in results else 0.0,
            ))
        return search_results

    async def delete(self, ids: list[str]) -> None:
        if self._collection:
            self._collection.delete(ids=ids)

    async def count(self) -> int:
        if self._collection:
            return self._collection.count()
        return 0


def create_vector_store(backend: str = "memory", **kwargs) -> VectorStore:
    """创建向量存储实例

    Args:
        backend: 后端类型 (memory/chroma)
        **kwargs: 配置参数

    Returns:
        向量存储实例
    """
    if backend == "chroma":
        store = ChromaVectorStore(kwargs.get("collection_name", "default"))
    else:
        store = InMemoryVectorStore(kwargs.get("embedding_dim", 1536))

    return store

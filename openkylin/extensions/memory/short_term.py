"""短期记忆 - Short Term Memory

会话级别的上下文记忆。
"""

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from openkylin.core.message import Message


@dataclass
class MemoryItem:
    """记忆项"""
    content: str
    role: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)


class ShortTermMemory:
    """短期记忆 - 会话上下文

    用于存储当前会话的消息历史，支持滑动窗口。
    """

    def __init__(self, max_size: int = 100):
        """
        Args:
            max_size: 最大记忆条数
        """
        self._max_size = max_size
        self._memory: deque[MemoryItem] = deque(maxlen=max_size)
        self._session_id: str | None = None

    @property
    def session_id(self) -> str | None:
        return self._session_id

    def start_session(self, session_id: str) -> None:
        """开始新会话"""
        self._session_id = session_id
        self._memory.clear()

    def add_message(self, message: Message) -> None:
        """添加消息到记忆"""
        self._memory.append(MemoryItem(
            content=message.content,
            role=message.role.value if hasattr(message.role, 'value') else str(message.role),
            timestamp=message.timestamp,
            metadata=message.metadata,
        ))

    def add(self, content: str, role: str = "user", metadata: dict[str, Any] | None = None) -> None:
        """直接添加记忆"""
        self._memory.append(MemoryItem(
            content=content,
            role=role,
            metadata=metadata or {},
        ))

    def get_messages(self, limit: int | None = None) -> list[Message]:
        """获取记忆消息"""
        items = list(self._memory)
        if limit:
            items = items[-limit:]

        return [
            Message(
                role=item.role,
                content=item.content,
                metadata=item.metadata,
                timestamp=item.timestamp,
            )
            for item in items
        ]

    def get_context(self, limit: int | None = None) -> str:
        """获取格式化的上下文"""
        messages = self.get_messages(limit)
        return "\n".join([
            f"{msg.role}: {msg.content}"
            for msg in messages
        ])

    def search(self, query: str, limit: int = 5) -> list[MemoryItem]:
        """搜索记忆"""
        # 简单实现：关键词匹配
        results = []
        for item in reversed(self._memory):
            if query.lower() in item.content.lower():
                results.append(item)
                if len(results) >= limit:
                    break
        return results

    def clear(self) -> None:
        """清空记忆"""
        self._memory.clear()

    def __len__(self) -> int:
        return len(self._memory)

    def __contains__(self, content: str) -> bool:
        return any(item.content == content for item in self._memory)

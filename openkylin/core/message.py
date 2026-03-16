"""统一消息抽象 - Unified Message Abstraction"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class Role(str, Enum):
    """消息角色"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass
class Message:
    """统一消息结构

    Attributes:
        role: 消息角色 (system/user/assistant/tool)
        content: 消息内容
        metadata: 元数据（渠道、来源、时间等）
        channel: 来源渠道标识
        timestamp: 时间戳
    """
    role: Role | str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    channel: str = "console"
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """转换为字典格式"""
        return {
            "role": self.role.value if isinstance(self.role, Role) else self.role,
            "content": self.content,
            "metadata": self.metadata,
            "channel": self.channel,
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Message":
        """从字典创建消息"""
        role = data.get("role", "user")
        if isinstance(role, str):
            role = Role(role) if role in [r.value for r in Role] else role

        return cls(
            role=role,
            content=data.get("content", ""),
            metadata=data.get("metadata", {}),
            channel=data.get("channel", "console"),
            timestamp=datetime.fromisoformat(data["timestamp"]) if data.get("timestamp") else datetime.now(),
        )

    def __str__(self) -> str:
        role_display = self.role.value if isinstance(self.role, Role) else self.role
        return f"[{role_display}] {self.content[:50]}{'...' if len(self.content) > 50 else ''}"

from dataclasses import dataclass, field
from typing import Any

from nonebot.adapters.onebot.v11 import Message, MessageSegment

@dataclass
class SendingBufferUnit:
    """
    发送缓冲区单元
    """
    message: str | Message | MessageSegment
    args: tuple[Any, ...] = field(default_factory=tuple)
    kwargs: dict[str, Any] = field(default_factory=dict)
    time: int = 0
    monotonic_time: int = 0
    reply: bool = True
    break_code: int = 0
    continue_handler: bool = False
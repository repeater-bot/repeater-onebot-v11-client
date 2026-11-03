import uuid
from typing import Protocol
from dataclasses import dataclass
from nonebot.adapters.onebot.v11 import MessageEvent, Message

@dataclass
class ETCHandlerResult:
    messages: list[Message]
    rendered_texts: list[str]
    retcode: int

class ETCCallbackType(Protocol):
    async def __call__(
        self,
        handler: str,
        event: MessageEvent,
        args: Message | None,
        output: bool = True,
    ) -> ETCHandlerResult:
        ...
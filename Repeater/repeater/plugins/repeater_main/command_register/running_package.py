import uuid
import asyncio
from typing import (
    TypeVar,
    Generic,
    Type,
    Generator,
    Any
)
from .package import CommandPackage
from ..assist import PersonaInfo, SendMsg
from nonebot.matcher import Matcher
from dataclasses import dataclass

T = TypeVar("T")

@dataclass
class RunningPackage(Generic[T]):
    """
    运行中的命令包
    """
    task_id: uuid.UUID
    start_time: int
    start_monotonic_time: int
    package: CommandPackage[T]
    matcher: Type[Matcher] | None
    persona_info: PersonaInfo
    send_msg: SendMsg
    task: asyncio.Task[T | Any]

    def __hash__(self) -> int:
        return hash((type(self), self.task_id, self.task))
    
    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, RunningPackage):
            return self.task_id == __o.task_id and self.task == __o.task
        return False

    def __await__(self) -> Generator[Any, None, T | Any]:
        yield from self.task.__await__()
    
    def cancel(self):
        self.task.cancel()
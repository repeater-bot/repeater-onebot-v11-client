import uuid
import asyncio

from typing import (
    Generic,
    AsyncGenerator,
    TypeVar
)
from ..exceptions import PipeCloseException

from dataclasses import dataclass

T_UPSTREAM = TypeVar("T_UPSTREAM")
T_DOWNSTREAM = TypeVar("T_DOWNSTREAM")

class ClosePipe:
    pass

@dataclass
class PipePackage(Generic[T_UPSTREAM, T_DOWNSTREAM]):
    """
    PipePackage
    """
    upstream: asyncio.Queue[T_UPSTREAM | ClosePipe]
    """Upstream queue."""
    downstream: asyncio.Future[asyncio.Queue[T_DOWNSTREAM]]
    """Downstream queue."""

    name: str
    """Package name."""
    sponsor: uuid.UUID
    """Sponsor task_id."""
    id: uuid.UUID
    """Package id."""
    other_id: uuid.UUID | None = None
    """Other package id."""

    async def wait_open(self) -> None:
        """
        Wait pipe open.
        """
        await self.downstream

    def opened(self) -> bool:
        """
        Check if pipe is opened.
        """
        return self.downstream.done()

    def closed(self) -> bool:
        """
        Check if pipe is closed.
        """
        return not self.opened()

    async def close(self) -> None:
        """
        Close pipe.
        """
        await self.upstream.put(ClosePipe())

    @property
    def downstream_queue(self) -> asyncio.Queue[T_DOWNSTREAM]:
        """
        Get downstream queue.
        """
        return self.downstream.result()

    async def next(self) -> T_DOWNSTREAM:
        """
        Get next data from upstream datas.
        """
        if self.closed():
            raise RuntimeError("Pipe not opened.")

        value = await self.downstream_queue.get()
        if isinstance(value, ClosePipe):
            raise PipeCloseException("Pipe closed.")
        return value

    async def send(self, data: T_UPSTREAM) -> None:
        """
        Send data to downstream datas.
        """
        if self.closed():
            raise RuntimeError("Pipe not opened.")
        
        await self.upstream.put(data)

    async def stream(self) -> AsyncGenerator[T_DOWNSTREAM, T_UPSTREAM]:
        """
        Stream data from upstream datas.
        """
        await self.wait_open()
        while True:
            data: T_DOWNSTREAM | ClosePipe = await self.downstream_queue.get()
            if isinstance(data, ClosePipe):
                break
            else:
                send_data = yield data
                await self.send(send_data)
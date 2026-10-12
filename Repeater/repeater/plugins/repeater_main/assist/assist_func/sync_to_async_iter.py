import asyncio
from typing import Iterable, Iterator, TypeVar, Generic, Self

T = TypeVar("T")

class SyncToAsyncIter(Generic[T]):
    """
    Sync to async iterator.
    """
    def __init__(self, sync_iter: Iterable[T]):
        self._sync_iter: Iterator[T] = iter(sync_iter)

    def __iter__(self) -> Iterator[T]:
        return self

    def __next__(self) -> T:
        return next(self._sync_iter)

    def __aiter__(self) -> Self:
        return self

    async def __anext__(self) -> T:
        try:
            return await asyncio.to_thread(
                next,
                self._sync_iter
            )
        except StopIteration:
            raise StopAsyncIteration
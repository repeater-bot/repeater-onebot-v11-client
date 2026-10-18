import os
from typing import AsyncGenerator, AsyncIterable, Iterable, Generic, TypeVar
from abc import abstractmethod
from pathlib import Path
from .._sync_base_storage import SyncStorage
from ...logger import logger

T_STORAGE_DATA = TypeVar("T_STORAGE_DATA")

class AsyncStorage(SyncStorage, Generic[T_STORAGE_DATA]):
    """
    Storage

    文件存储管理器
    """
    
    async def load(self, path: str | os.PathLike) -> T_STORAGE_DATA:
        path = self.path(path)
        self._total_read_count += 1
        if path in self.storage_cache:
            self._cache_hit_read_count += 1
            logger.info(
                "Cache hit read (Hit rate: {cache_hit_read_rate:.2%})",
                cache_hit_read_rate = self._cache_hit_read_count / (self._total_read_count)
            )
            return self.storage_cache[path]
        else:
            logger.info(
                "Cache miss read (Hit rate: {cache_miss_read_rate:.2%})",
                cache_miss_read_rate = self._cache_hit_read_count / (self._total_read_count)
            )
            data = await self._load(path)
            self.storage_cache[path] = data
            return data
    
    async def save(self, path: str | os.PathLike, data: T_STORAGE_DATA, append: bool = False) -> None:
        path = self.path(path)
        self.storage_cache[path] = data
        path.parent.mkdir(parents=True, exist_ok=True)
        await self._save(path, data, append = append)

    async def load_line_stream(self, path: str | os.PathLike) -> AsyncGenerator[T_STORAGE_DATA, None]:
        path = self.path(path)
        async for line in self._load_line_stream(path):
            yield line

    async def load_stream(self, path: str | os.PathLike) -> AsyncGenerator[T_STORAGE_DATA, None]:
        path = self.path(path)
        async for line in self._load_stream(path):
            yield line

    async def save_stream(self, path: str | os.PathLike, data: Iterable[T_STORAGE_DATA], append: bool = False) -> None:
        path = self.path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        await self._save_stream(path, data, append = append)

    async def save_astream(self, path: str | os.PathLike, data: AsyncIterable[T_STORAGE_DATA], append: bool = False) -> None:
        path = self.path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        await self._save_astream(path, data, append = append)
    
    @abstractmethod
    async def _load(self, path: Path) -> T_STORAGE_DATA:
        raise NotImplementedError
    
    @abstractmethod
    async def _save(self, path: Path, data: T_STORAGE_DATA, append: bool = False) -> None:
        raise NotImplementedError

    @abstractmethod
    async def _load_line_stream(self, path: Path) -> AsyncGenerator[T_STORAGE_DATA, None]:
        raise NotImplementedError

    @abstractmethod
    async def _load_stream(self, path: Path) -> AsyncGenerator[T_STORAGE_DATA, None]:
        raise NotImplementedError

    @abstractmethod
    async def _save_stream(self, path: Path, data: Iterable[T_STORAGE_DATA], append: bool = False) -> None:
        raise NotImplementedError

    @abstractmethod
    async def _save_astream(self, path: Path, data: AsyncIterable[T_STORAGE_DATA], append: bool = False) -> None:
        raise NotImplementedError
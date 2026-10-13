import os
import shutil
from pathlib import Path
from typing import AsyncGenerator, Generator, Iterable, Generic, TypeVar
from abc import ABC, abstractmethod
from cachetools import LRUCache
from ...logger import logger

T_STORAGE_DATA = TypeVar("T_STORAGE_DATA")

class SyncStorage(ABC, Generic[T_STORAGE_DATA]):
    """
    Storage

    文件存储管理器
    """
    storage_cache: LRUCache[str | os.PathLike, T_STORAGE_DATA] = LRUCache(maxsize=1000)
    _total_read_count: int = 0
    _cache_hit_read_count: int = 0

    def __init__(self, storage_base_path: str | Path):
        """
        :param storage_base_path: 存储路径
        """
        self.storage_base_path = Path(storage_base_path)
    
    def path(self, path: str | os.PathLike | None = None):
        if path is None:
            return self.storage_base_path
        else:
            path = Path(path)
            if path.is_absolute():
                return path
            return self.storage_base_path / path
    
    def load(self, path: str | os.PathLike) -> T_STORAGE_DATA:
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
            data = self._load(path)
            self.storage_cache[path] = data
            return data
    
    def save(self, path: str | os.PathLike, data: T_STORAGE_DATA) -> None:
        self.storage_cache[path] = data
        self._save(path, data)

    @abstractmethod
    def load_line_stream(self, path: str | os.PathLike) -> AsyncGenerator[T_STORAGE_DATA, None]:
        pass
        
    @abstractmethod
    def load_stream(self, path: str | os.PathLike) -> AsyncGenerator[T_STORAGE_DATA, None]:
        pass

    @abstractmethod
    def save_stream(self, path: str | os.PathLike, data: Iterable[T_STORAGE_DATA]) -> None:
        pass

    @abstractmethod
    def _load(self, path: str | os.PathLike) -> T_STORAGE_DATA:
        pass
    
    @abstractmethod
    def _save(self, path: str | os.PathLike, data: T_STORAGE_DATA) -> None:
        pass

    def move(self, src: str | os.PathLike, dst: str | os.PathLike) -> None:
        src = self.path(src)
        dst = self.path(dst)
        src.rename(dst)
    
    def remove(self, path: str | os.PathLike) -> None:
        path = self.path(path)
        if path.exists():
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                shutil.rmtree(path)
    
    def copy(self, src: str | os.PathLike, dst: str | os.PathLike) -> None:
        src = self.path(src)
        dst = self.path(dst)
        if src.is_file():
            shutil.copy(src, dst)
        elif src.is_dir():
            shutil.copytree(src, dst)
    
    def exists(self, path: str | os.PathLike | None = None) -> bool:
        path = self.path(path)
        return path.exists()

    def is_file(self, path: str | os.PathLike | None = None) -> bool:
        path = self.path(path)
        return path.is_file()

    def is_dir(self, path: str | os.PathLike | None = None) -> bool:
        path = self.path(path)
        return path.is_dir()

    def glob(self, glob: str, path: str | os.PathLike | None = None) -> list[Path]:
        path = self.path(path)
        return [f for f in path.glob(glob)]

    def rglob(self, glob: str, path: str | os.PathLike | None = None) -> list[Path]:
        path = self.path(path)
        return [f.relative_to(self.storage_base_path) for f in path.rglob(glob)]

    def list(self, path: str | os.PathLike | None = None) -> list[Path]:
        path = self.path(path)
        return [f for f in path.iterdir()]

    def iterdir(self, path: str | os.PathLike | None = None) -> Generator[Path, None, None]:
        path = self.path(path)
        return path.iterdir()
import aiofiles
from pathlib import Path
from typing import AsyncGenerator, AsyncIterable, Iterable
from ._storage import AsyncStorage
from ...logger import logger as base_logger

logger = base_logger.bind(module = "Storage.Async.Text")

class TextStorage(AsyncStorage[str]):
    async def _load(self, path: Path, encoding: str = "utf-8") -> str:
        try:
            logger.info(f"Load {path}")
            async with aiofiles.open(path, "r", encoding = encoding) as f:
                return await f.read()
        except Exception as e:
            logger.error(f"Load {path} failed: {e}")
            raise
    
    async def _load_line_stream(self, path: Path, encoding: str = "utf-8") -> AsyncGenerator[str, None]:
        try:
            logger.info(f"Use line-by-line chunk streaming to load the file \"{path}\"")
            async with aiofiles.open(path, "r", encoding = encoding) as f:
                async for line in f:
                    yield line
        except Exception as e:
            logger.error(f"Load {path} failed: {e}")
            raise
    
    async def _load_stream(self, path: Path, encoding: str = "utf-8", chunk_size: int = 1024) -> AsyncGenerator[str, None]:
        try:
            logger.info(f"Stream load the file \"{path}\" in {chunk_size}-byte chunks")
            async with aiofiles.open(path, "r", encoding=encoding) as f:
                while True:
                    chunk = await f.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk
        except Exception as e:
            logger.error(f"Load {path} failed: {e}")
            raise

    async def _save(self, path: Path, data: str, encoding: str = "utf-8", append: bool = False) -> None:
        try:
            logger.info(f"Saving text to {path}")
            if not path.parent.exists():
                path.parent.mkdir(parents=True)
            async with aiofiles.open(path, "w" if not append else "a", encoding=encoding) as f:
                await f.write(data)
        except Exception as e:
            logger.error(f"Save {path} failed: {e}")
            raise
    
    async def _save_stream(self, path: Path, data: Iterable[str], encoding: str = "utf-8", append: bool = False) -> None:
        try:
            logger.info(f"Saving text stream to {path}")
            if not path.parent.exists():
                path.parent.mkdir(parents=True)
            async with aiofiles.open(path, "w" if not append else "a", encoding=encoding) as f:
                for line in data:
                    await f.write(line)
        except Exception as e:
            logger.error(f"Save {path} failed: {e}")
            raise
    
    async def _save_astream(self, path: Path, data: AsyncIterable[str], encoding: str = "utf-8", append: bool = False) -> None:
        try:
            logger.info(f"Saving text async stream to {path}")
            if not path.parent.exists():
                path.parent.mkdir(parents=True)
            async with aiofiles.open(path, "w" if not append else "a", encoding=encoding) as f:
                async for line in data:
                    await f.write(line)
        except Exception as e:
            logger.error(f"Save {path} failed: {e}")
            raise
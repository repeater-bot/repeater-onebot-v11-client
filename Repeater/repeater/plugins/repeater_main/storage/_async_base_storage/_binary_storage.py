import aiofiles
from typing import AsyncGenerator, AsyncIterable, Iterable
from pathlib import Path
from ._storage import AsyncStorage
from ...logger import logger as base_logger

logger = base_logger.bind(module = "Storage.Async.Binary")

class BinaryStorage(AsyncStorage[bytes]):
    async def _load(self, path: Path) -> bytes:
        try:
            logger.info(f"Loading binary from {path}")
            async with aiofiles.open(path, "rb") as f:
                return await f.read()
        except Exception as e:
            logger.error(f"Error loading binary from {path}: {e}")
            raise
    
    async def _load_line_stream(self, path: Path) -> AsyncGenerator[bytes, None]:
        try:
            logger.info(f"Use line-by-line chunk streaming to load the file \"{path}\"")
            async with aiofiles.open(path, "rb") as f:
                async for line in f:
                    yield line
        except Exception as e:
            logger.error(f"Error loading binary line stream from {path}: {e}")
            raise
    
    async def _load_stream(self, path: Path, chunk_size: int = 1024) -> AsyncGenerator[bytes, None]:
        try:
            logger.info(f"Stream load the file \"{path}\" in {chunk_size}-byte chunks")
            async with aiofiles.open(path, "rb") as f:
                while True:
                    chunk = await f.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk
        except Exception as e:
            logger.error(f"Error loading binary stream from {path}: {e}")
            raise
    
    async def _save(self, path: Path, data: bytes, append: bool = False) -> None:
        try:
            logger.info(f"Saving binary to {path}")
            async with aiofiles.open(path, "wb" if not append else "ab") as f:
                await f.write(data)
        except Exception as e:
            logger.error(f"Error saving binary to {path}: {e}")
            raise
    
    async def _save_stream(self, path: Path, stream: Iterable[bytes], append: bool = False) -> None:
        try:
            logger.info(f"Saving binary stream to {path}")
            async with aiofiles.open(path, "wb" if not append else "ab") as f:
                for line in stream:
                    await f.write(line)
        except Exception as e:
            logger.error(f"Error saving binary stream to {path}: {e}")
            raise
    
    async def _save_astream(self, path: Path, stream: AsyncIterable[bytes], append: bool = False) -> None:
        try:
            logger.info(f"Saving binary stream to {path}")
            async with aiofiles.open(path, "wb" if not append else "ab") as f:
                async for line in stream:
                    await f.write(line)
        except Exception as e:
            logger.error(f"Error saving binary stream to {path}: {e}")
            raise
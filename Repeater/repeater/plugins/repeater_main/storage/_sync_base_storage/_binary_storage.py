from typing import Generator, Iterable
from pathlib import Path
from ._storage import SyncStorage
from ...logger import logger as base_logger

logger = base_logger.bind(module = "Storage.Sync.Binary")

class BinaryStorage(SyncStorage[bytes]):
    def _load(self, path: Path) -> bytes:
        try:
            logger.info(f"Loading binary from {path}")
            if not path.parent.exists():
                path.parent.mkdir(parents=True)
            with open(path, "rb") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error loading binary from {path}: {e}")
            raise
    
    def _load_line_stream(self, path: Path) -> Generator[bytes, None, None]:
        try:
            logger.info(f"Use line-by-line chunk streaming to load the file \"{path}\"")
            with open(path, "rb") as f:
                for line in f:
                    yield line
        except Exception as e:
            logger.error(f"Error loading binary line stream from {path}: {e}")
            raise
    
    def _load_stream(self, path: Path, chunk_size: int = 1024) -> Generator[bytes, None, None]:
        try:
            logger.info(f"Stream load the file \"{path}\" in {chunk_size}-byte chunks")
            with open(path, "rb") as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk
        except Exception as e:
            logger.error(f"Error loading binary stream from {path}: {e}")
            raise
    
    def _save(self, path: Path, data: bytes, append: bool = False) -> None:
        try:
            logger.info(f"Saving binary to {path}")
            if not path.parent.exists():
                path.parent.mkdir(parents=True)
            with open(path, "wb" if not append else "ab") as f:
                f.write(data)
        except Exception as e:
            logger.error(f"Error saving binary to {path}: {e}")
            raise
    
    def _save_stream(self, path: Path, stream: Iterable[bytes], append: bool = False) -> None:
        try:
            logger.info(f"Saving binary stream to {path}")
            if not path.parent.exists():
                path.parent.mkdir(parents=True)
            with open(path, "wb" if not append else "ab") as f:
                for line in stream:
                    f.write(line)
        except Exception as e:
            logger.error(f"Error saving binary stream to {path}: {e}")
            raise
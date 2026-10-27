from typing import Generator, Iterable
from pathlib import Path
from ._storage import SyncStorage
from ...logger import logger as base_logger

logger = base_logger.bind(module = "Storage.Sync.Text")

class TextStorage(SyncStorage[str]):
    def _load(self, path: Path, encoding: str = "utf-8") -> str:
        try:
            logger.info(f"Load {path}")
            with open(path, "r", encoding = encoding) as f:
                return f.read()
        except Exception as e:
            logger.error(f"Load {path} failed: {e}")
            raise
    
    def _load_line_stream(self, path: Path, encoding: str = "utf-8") -> Generator[str, None, None]:
        try:
            logger.info(f"Use line-by-line chunk streaming to load the file \"{path}\"")
            with open(path, "r", encoding = encoding) as f:
                for line in f:
                    yield line
        except Exception as e:
            logger.error(f"Load {path} failed: {e}")
            raise
    
    def _load_stream(self, path: Path, encoding: str = "utf-8", chunk_size: int = 1024) -> Generator[str, None, None]:
        try:
            logger.info(f"Stream load the file \"{path}\" in {chunk_size}-byte chunks")
            with open(path, "r", encoding=encoding) as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk
        except Exception as e:
            logger.error(f"Load {path} failed: {e}")
            raise

    def _save(self, path: Path, data: str, encoding: str = "utf-8", append: bool = False) -> None:
        try:
            logger.info(f"Saving text to {path}")
            if not path.parent.exists():
                path.parent.mkdir(parents=True)
            with open(path, "w" if not append else "a", encoding=encoding) as f:
                f.write(data)
        except Exception as e:
            logger.error(f"Save {path} failed: {e}")
            raise
    
    def _save_stream(self, path: Path, data: Iterable[str], encoding: str = "utf-8", append: bool = False) -> None:
        try:
            logger.info(f"Saving text stream to {path}")
            if not path.parent.exists():
                path.parent.mkdir(parents=True)
            with open(path, "w" if not append else "a", encoding=encoding) as f:
                for line in data:
                    f.write(line)
        except Exception as e:
            logger.error(f"Save {path} failed: {e}")
            raise
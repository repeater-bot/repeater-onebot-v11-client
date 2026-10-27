import os
import yaml
import asyncio
from ._async_base_storage import TextStorage
from typing import Any, TypeVar
from ..logger import logger as base_logger

logger = base_logger.bind(module = "Storage.Async.Yaml")

T = TypeVar("T")

class YamlStorage(TextStorage):
    """
    YAML Storage

    存储文件格式为 YAML
    """
    async def load_yaml(self, path: str | os.PathLike, default: T = None) -> Any | T:
        try:
            logger.info(f"Loading yaml from {path}")
            return await asyncio.to_thread(
                yaml.safe_load,
                await self.load(path)
            )
        except Exception as e:
            logger.error(f"load yaml error: {e}")
            return None
    
    async def save_yaml(self, path: str | os.PathLike, data: Any):
        try:
            logger.info(f"Saving yaml to {path}")
            await self.save(
                path,
                data = await asyncio.to_thread(
                    yaml.safe_dump,
                    data
                )
            )
        except Exception as e:
            logger.error(f"save yaml error: {e}")

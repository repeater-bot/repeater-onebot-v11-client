import os

from pydantic import BaseModel
from typing import Type, Any, TypeVar, Generic
from pathlib import Path
from ._mode import Mode
from ..storage import async_json_storage, async_yaml_storage, storage_path
from ..logger import logger as base_logger

logger = base_logger.bind(module = "Configs.Loader")

T_MODEL = TypeVar("T_MODEL", bound=BaseModel)

class AsyncLoader(Generic[T_MODEL]):
    def __init__(self, model: Type[T_MODEL], path: str | os.PathLike, mode: Mode = Mode.JSON):
        self._model: Type[T_MODEL] = model
        self._path = Path(path)
        self._mode: Mode = mode
    
    def get_storage_path(self) -> Path:
        return Path(storage_path.storage_base_path) / self._path
    
    def exists(self) -> bool:
        return self.get_storage_path().exists()
    
    async def load(self, unexist_create: bool = False, write_on_failure: bool = False) -> T_MODEL:
        if unexist_create and not self.exists():
            config = self._model()
            logger.warning(
                "Config {config_file} is not found, creating new one",
                config_file = self._path.as_posix()
            )
            await self.save(config)
            return config
        try:
            if self._mode == Mode.JSON:
                return self._model(**(await self._decode_json(self._path)))
            elif self._mode == Mode.YAML:
                return self._model(**(await self._decode_yaml(self._path)))
            else:
                raise ValueError("Unknown mode")
        except Exception as e:
            if write_on_failure:
                logger.warning(
                    "Failed to load config from \"{config_file}\", writing default config",
                    config_file = self._path.as_posix()
                )
                model = self._model()
                await self.save(model)
                return model
            else:
                raise e

    async def save(self, data: T_MODEL):
        if self._mode == Mode.JSON:
            return await self._encode_json(self._path, data.model_dump())
        elif self._mode == Mode.YAML:
            return await self._encode_yaml(self._path, data.model_dump())
        else:
            raise ValueError("Unknown mode")

    @staticmethod
    async def _decode_json(file_path: str | os.PathLike) -> Any:
        return await async_json_storage.load_json(file_path)

    @staticmethod
    async def _decode_yaml(file_path: str | os.PathLike) -> Any:
        return await async_yaml_storage.load_yaml(file_path)
    
    @staticmethod
    async def _encode_json(file_path: str | os.PathLike, data: Any) -> None:
        return await async_json_storage.save_json(file_path, data)

    @staticmethod
    async def _encode_yaml(file_path: str | os.PathLike, data: Any) -> None:
        return await async_yaml_storage.save_yaml(file_path, data)
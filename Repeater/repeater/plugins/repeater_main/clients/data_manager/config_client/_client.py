import httpx

from ....logger import logger as base_logger
from typing import (
    Any,
)
from ....assist import Response, PersonaInfo, http_transport
# 服务端配置
from ....client_configs import *

from .._base_user_data_client import UserDataClient

logger = base_logger.bind(module = "Config.Core")

class ConfigClient(UserDataClient):
    timeout = storage_configs.server_api_timeout.config
    data_type = "config"
    
    # region set config
    async def set_config(self, config_key: str, value: Any, item_type: str = "auto") -> Response[Any]:
        TYPES = {
            int: "int",
            float: "float",
            str: "string",
            bool: "boolean",
            dict: "dict",
            list: "list",
            None: "null"
        }
        if item_type == "raw":
            item_type = "raw"
        if item_type == "auto":
            if value is None:
                item_type = "null"
            elif type(value) not in TYPES:
                raise TypeError(f"Unsupported type: {type(value).__name__}")
            else:
                item_type = TYPES[type(value)]
        else:
            if item_type not in TYPES:
                raise TypeError(f"Unsupported type: {item_type}")
        logger.info(
            "Set config: {config_key} = {value}(type:{item_type})",
            config_key=config_key,
            value=value,
            item_type=item_type
        )
        response = await self.client.put(
            self.join_url_static(SET_CONFIG_ROUTE, self.namespace_str, config_key),
            json={
                "type": item_type,
                "value": value
            }
        )
        return Response(response)
    # endregion

    # region get config
    async def get_configs(self) -> Response[Any | None]:
        logger.info("Get {user} configs", user=self.namespace_str)
        response = await self.client.get(
            self.join_url_static(GET_CONFIG_ROUTE, self.namespace_str)
        )
        return Response(response)
    
    def get_configs_url(self) -> str:
        return self.join_url(GET_CONFIG_ROUTE, f"{self.namespace_str}.json")
    # endregion

    # region remove config key
    async def remove_config_key(self, config_key: str) -> Response[None]:
        logger.info("Remove config key: {config_key}", config_key=config_key)
        response = await self.client.delete(
            self.join_url_static(REMOVE_CONFIG_KEY_ROUTE, self.namespace_str, config_key)
        )
        return Response(response)
    # endregion
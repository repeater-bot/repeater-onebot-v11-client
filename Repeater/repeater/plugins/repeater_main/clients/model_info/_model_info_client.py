import httpx
from urllib.parse import quote
from ...logger import logger as base_logger
from typing import (
    Any,
)

from ...client_configs import *
from ...assist import Response, BaseClient
from ._models import (
    ModelsResponse,
    PingProviderResponse,
    RefreshResponse
)

logger = base_logger.bind(module = "Config.Core")

class ModelInfoClient(BaseClient):
    timeout = storage_configs.server_api_timeout.model_info
    
    # region get all models
    async def get_all_models(self) -> Response[ModelsResponse]:
        response = await self.client.get(
            GET_MODEL_LIST,
        )
        return Response(
            httpx_response = response,
            model = ModelsResponse,
        )
    # endregion

    # region get models
    async def get_models(self, model_uid: str) -> Response[ModelsResponse]:
        response = await self.client.get(
            self.join_url_static(GET_MODEL_LIST, model_uid),
        )
        return Response(
            httpx_response = response,
            model = ModelsResponse,
        )
    # endregion

    # region ping provider
    async def ping_provider(
            self,
            user_id: str,
            model_id: str | list[str] | None = None,
            timeout: float = 5.0,
            times: int = 4,
            size: int = 32,
            interval: int = 0
        ) -> Response[PingProviderResponse]:
        response = await self.client.post(
            self.join_url_static(PING_PROVIDER, user_id),
            json = {
                "model_id": model_id,
                "timeout": timeout, 
                "times": times, 
                "size": size,
                "interval": interval
            }
        )
        return Response(
            httpx_response = response,
            model = PingProviderResponse,
        )
    # endregion

    # region refresh
    async def refresh(self, provider_id: str | None = None) -> Response[RefreshResponse]:
        url = self.join_url(REFRESH)
        if provider_id is not None:
            url = self.join_url_static(REFRESH, provider_id)

        response = await self.client.post(
            url
        )
        return Response(
            httpx_response = response,
            model = RefreshResponse,
        )
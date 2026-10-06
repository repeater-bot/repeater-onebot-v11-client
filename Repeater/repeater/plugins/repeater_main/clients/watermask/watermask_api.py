from ...client_configs import *
from ...assist import Response, BaseClient
from .request import WatermaskEncodeRequest, WatermaskDecodeRequest
from .response import WatermaskDecodeResponse

class WatermaskClient(BaseClient):
    timeout = storage_configs.server_api_timeout.watermask

    async def encode(
            self,
            text: str,
            image: str,
        ) -> Response[bytes]:
        response = await self.client.post(
            url = self.join_url(SIMILARITY_ROUTE, self._persona_info.namespace_str),
            json = WatermaskEncodeRequest(
                text = text,
                image = image,
            ).model_dump(exclude_none = True)
        )
        return Response(
            httpx_response = response
        )

    async def decode(
            self,
            image: str
        ) -> Response[WatermaskDecodeResponse]:
        response = await self.client.post(
            url = self.join_url(VECTORS_ROUTE, self._persona_info.namespace_str),
            json = WatermaskDecodeRequest(
                image = image
            ).model_dump(exclude_none = True)
        )
        return Response(
            httpx_response = response,
            model = WatermaskDecodeResponse
        )
from ...client_configs import *
from ...assist import Response, BaseClient
from .request import WatermaskEncodeRequest, WatermaskDecodeRequest
from .response import WatermaskDecodeResponse

class WatermarkClient(BaseClient):
    timeout = storage_configs.server_api_timeout.watermark

    async def encode(
            self,
            text: str,
            image: str,
        ) -> Response[bytes]:
        response = await self.client.post(
            url = self.join_url(WATERMARK_ENCODE_ROUTE),
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
            url = self.join_url(WATERMARK_DECODE_ROUTE),
            json = WatermaskDecodeRequest(
                image = image
            ).model_dump(exclude_none = True)
        )
        return Response(
            httpx_response = response,
            model = WatermaskDecodeResponse
        )
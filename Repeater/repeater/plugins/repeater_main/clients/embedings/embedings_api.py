from ...client_configs import *
from ...assist import Response, BaseClient
from .request import SimilarityRequest, VectorsRequest
from .response import SimilarityResponse, VectorsResponse

class EmbedingsClient(BaseClient):
    timeout = storage_configs.server_api_timeout.embeding

    async def similarity(
            self,
            first_text: str,
            second_text: str,
            model: str | None = None
        ) -> Response[SimilarityResponse]:
        response = await self.client.post(
            url = self.join_url(SIMILARITY_ROUTE, self._persona_info.namespace_str),
            json = SimilarityRequest(
                first_text = first_text,
                second_text = second_text,
                model = model,
            ).model_dump(exclude_none = True)
        )
        return Response(
            httpx_response = response,
            model = SimilarityResponse
        )

    async def vectors(
            self,
            texts: list[str],
            model: str | None = None
        ) -> Response[VectorsResponse]:
        response = await self.client.post(
            url = self.join_url(VECTORS_ROUTE, self._persona_info.namespace_str),
            json = VectorsRequest(
                texts = texts,
                model = model,
            ).model_dump(exclude_none = True)
        )
        return Response(
            httpx_response = response,
            model = VectorsResponse
        )
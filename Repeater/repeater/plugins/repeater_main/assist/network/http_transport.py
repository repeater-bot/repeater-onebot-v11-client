import curlify2

from httpx import (
    AsyncHTTPTransport,
    Request,
    Response
)
from .ssl import ssl_context
from loguru import logger
from ...client_configs import storage_configs

class HTTPTransport(AsyncHTTPTransport):
    async def handle_async_request(self, request: Request) -> Response:
        curlify = curlify2.Curlify(request)
        logger.info(
            "Sending request: \n{curl_str}\n",
            curl_str = curlify.to_curl(),
        )
        return await super().handle_async_request(request)

http_transport = HTTPTransport(
    verify = ssl_context.get_ssl_context(),
    limits = storage_configs.client_limits.to_limits(),
)
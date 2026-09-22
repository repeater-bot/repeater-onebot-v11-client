import httpx
import orjson
from ...logger import logger as base_logger

from ...client_configs import *
from ._request_log_object import RequestLog
from ...assist import BaseClient

logger = base_logger.bind(module = "Config.Core")

class RequestLogClient(BaseClient):
    timeout = storage_configs.server_api_timeout.request_log
    
    async def get_request_log(self):
        async with self.client.stream(
            method = "GET",
            url = REQUEST_LOG_STREAM_ROUTE
        ) as response:
            response.raise_for_status()
            async for chunk in response.aiter_lines():
                chunk_data = orjson.loads(chunk)
                yield RequestLog(**chunk_data)
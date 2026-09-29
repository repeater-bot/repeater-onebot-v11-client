import time
import httpx
from ...logger import logger
from ..network import http_transport

class Downloader:
    global_client: httpx.AsyncClient = httpx.AsyncClient(
        transport = http_transport,
    )

    def __init__(self, usage_global_client: bool = True):
        self.client: httpx.AsyncClient

        if usage_global_client:
            self.client = self.global_client
        else:
            self.client = httpx.AsyncClient(
                transport = http_transport,
            )

    async def download_text(self, url: str, timeout: int | float | None = 5) -> str:
        start_time = time.perf_counter_ns()
        try:
            response = await self.client.get(
                url,
                timeout = timeout
            )
            response.raise_for_status()
        finally:
            end_time = time.perf_counter_ns()
            logger.info(
                "Downloaded text from {url} in {time:.2f}ms",
                url = url,
                time = (end_time - start_time) / 1e6
            )
        return response.text

    async def download_file(self, url: str, timeout: int | float | None = 5) -> bytes:
        start_time = time.perf_counter_ns()
        try:
            response = await self.client.get(
                url,
                timeout = timeout
            )
            response.raise_for_status()
        finally:
            end_time = time.perf_counter_ns()
            logger.info(
                "Downloaded file from {url} in {time:.2f}ms",
                url = url,
                time = (end_time - start_time) / 1e6
            )
        return response.content

    async def close(self):
        await self.client.aclose()

from typing import AsyncGenerator
from ...assist import BaseClient, ClientInfo
from ...client_configs import storage_configs, ALIVED_ROUTE, ALIVED_TIME_NS

class AlivedClient(BaseClient):
    
    def __post_init__(self):
        client_info = ClientInfo(
            url = "",
            follow_redirects = self.follow_redirects,
            timeout = self.timeout,
            encoding = self.encoding
        )

        self.client = self._httpx_clients.get_client(client_info)

    async def check_alive(self, backend: str) -> bool:
        backends = storage_configs.backends

        if backend not in backends:
            raise ValueError("backend not found")

        response = await self.client.get(
            url = self.join_url_static(
                ALIVED_ROUTE,
                base_url = backends[backend]
            )
        )

        return response.status_code == 200

    async def check_alives(self) -> dict[str, bool]:
        alives: dict[str, bool] = {}

        async for backend, alived in self.check_aliveds_stream():
            alives[backend] = alived

        return alives

    async def check_aliveds_stream(self) -> AsyncGenerator[tuple[str, bool], None]:
        for backend, url in storage_configs.backends.items():
            response = await self.client.get(
                url = self.join_url_static(
                    ALIVED_ROUTE,
                    base_url = url
                )
            )

            yield backend, response.status_code == 200

    async def alived_time(self, backend: str) -> int:
        backends = storage_configs.backends

        if backend not in backends:
            raise ValueError("backend not found")

        response = await self.client.get(
            url = self.join_url_static(
                ALIVED_TIME_NS,
                base_url = backends[backend]
            )
        )

        return int(response.text)

    async def alived_times(self) -> dict[str, int]:
        alived_times: dict[str, int] = {}

        async for backend, alived_time in self.alived_times_stream():
            alived_times[backend] = alived_time

        return alived_times

    async def alived_times_stream(self) -> AsyncGenerator[tuple[str, int], None]:
        for backend, url in storage_configs.backends.items():
            response = await self.client.get(
                url = self.join_url_static(
                    ALIVED_TIME_NS,
                    base_url = url
                )
            )

            yield backend, int(response.text)
        

        
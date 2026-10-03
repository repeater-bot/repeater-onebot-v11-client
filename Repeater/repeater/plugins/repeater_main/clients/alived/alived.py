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
                backends[backend],
                ALIVED_ROUTE
            )
        )

        return response.status_code == 200

    async def check_alives(self) -> dict[str, bool]:
        alives: dict[str, bool] = {}

        for backend, url in storage_configs.backends.items():
            response = await self.client.get(
                url = self.join_url_static(
                    url,
                    ALIVED_ROUTE
                )
            )

            alives[backend] = response.status_code == 200

        return alives

    async def alived_time(self, backend: str) -> int:
        backends = storage_configs.backends

        if backend not in backends:
            raise ValueError("backend not found")

        response = await self.client.get(
            url = self.join_url_static(
                backends[backend],
                ALIVED_TIME_NS
            )
        )

        return int(response.text)

    async def alived_times(self) -> dict[str, int]:
        alived_times: dict[str, int] = {}

        for backend, url in storage_configs.backends.items():
            response = await self.client.get(
                url = self.join_url_static(
                    url,
                    ALIVED_TIME_NS
                )
            )

            alived_times[backend] = int(response.text)

        return alived_times
        

        
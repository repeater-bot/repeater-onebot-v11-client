from pydantic import BaseModel
from httpx import AsyncClient, Limits, Timeout
from ._timeout import ClientTimeout
from ...network import http_transport

class ClientInfo(BaseModel, frozen=True):
    url: str = ""
    follow_redirects: bool = True
    timeout: int | float | ClientTimeout | None = 5.0
    encoding: str = "utf-8"

    def _default_limits(self) -> Limits:
        return Limits(
            max_connections = 100,
            max_keepalive_connections = 20
        )
    
    def _default_timeout(self) -> Timeout:
        return Timeout(
            timeout = 5.0
        )

    def to_client(
        self,
        params: dict[str, str | int | float | bool | None] | None = None,
        headers: dict[str, str] | None = None,
        cookies: dict[str, str] | None = None,
        auth: tuple[str, str] | None = None
    ) -> AsyncClient:
        if self.timeout is None:
            timeout = None
        if isinstance(self.timeout, int | float):
            timeout = self.timeout
        elif isinstance(self.timeout, ClientTimeout):
            timeout = self.timeout.to_timeout()
        else:
            timeout = self._default_timeout()
        
        client = AsyncClient(
            base_url = self.url,
            params = params,
            headers = headers,
            cookies = cookies,
            auth = auth,
            follow_redirects = self.follow_redirects,
            transport = http_transport,
            timeout = timeout,
            default_encoding = self.encoding
        )
        return client
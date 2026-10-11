from httpx import Limits
from pydantic import BaseModel

class ClientLimits(BaseModel, frozen=True):
    max_connections: int | None = None
    max_keepalive_connections: int | None = None
    keepalive_expiry: int | float | None = 5

    def to_limits(self) -> Limits:
        return Limits(
            max_connections = self.max_connections,
            max_keepalive_connections = self.max_keepalive_connections,
            keepalive_expiry = self.keepalive_expiry
        )
from pydantic import BaseModel, Field
from .ping_provider_statistics import PingProviderStatisics

class PingProviderDetails(BaseModel):
    host_names: list[str] = Field(default_factory=list)
    ip: str | None = None
    time: list[float] = Field(default_factory=list)
    packet_loss: float = 0.0
    max_time: float = 0.0
    min_time: float = 0.0
    avg_time: float = 0.0

    def to_statistics(self) -> PingProviderStatisics:
        return PingProviderStatisics(self.time)
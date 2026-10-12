from pydantic import BaseModel, Field
from .limit_speed_per_minute import LimitSpeedPerMinute

class Camouflage(BaseModel):
    limit_speed_per_minute: LimitSpeedPerMinute = Field(default_factory=LimitSpeedPerMinute)
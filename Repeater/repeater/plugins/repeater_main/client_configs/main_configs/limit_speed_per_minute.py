from pydantic import BaseModel


class LimitSpeedPerMinute(BaseModel):
    """
    Limit speed per minute
    """
    send_msg: int | float | None = 100
    file: int | float | None = 50
    poke: int | float | None = 6
    zone: int | float | None = 20
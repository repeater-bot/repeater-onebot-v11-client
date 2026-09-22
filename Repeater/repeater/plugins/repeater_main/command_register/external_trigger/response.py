from pydantic import BaseModel


class ExternalTriggerResponse(BaseModel):
    """
    Response for external trigger
    """
    messages: list[str] = []
    error: str | None = None
    retcode: int = 0
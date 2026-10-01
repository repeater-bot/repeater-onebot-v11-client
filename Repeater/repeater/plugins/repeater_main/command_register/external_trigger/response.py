from pydantic import BaseModel, Field

class ExternalTriggerResponse(BaseModel):
    """
    Response for external trigger
    """
    messages: list[str] = Field(default_factory=list)
    rendered_texts: list[str] = Field(default_factory=list)
    error: str | None = None
    retcode: int = 0
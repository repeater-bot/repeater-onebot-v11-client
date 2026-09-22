from pydantic import BaseModel
from .event import MessageEventModel

class ExternalTriggerRequest(BaseModel):
    """
    External trigger request model
    """
    bot_id: str
    handler: str
    event_data: MessageEventModel
    args: str | None = None
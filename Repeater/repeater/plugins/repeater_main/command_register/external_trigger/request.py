from pydantic import BaseModel
from nonebot.adapters.onebot.v11 import MessageEvent

class ExternalTriggerRequest(BaseModel):
    """
    External trigger request model
    """
    bot_id: str
    handler: str
    event_data: MessageEvent
    args: str | None = None
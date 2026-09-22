from pydantic import BaseModel, ConfigDict
from nonebot.adapters.onebot.v11.event import Sender, Reply as NonebotReply
from nonebot.adapters.onebot.v11 import Message

class Reply(BaseModel):
    model_config = ConfigDict(extra="allow")

    time: int
    message_type: str
    message_id: int
    real_id: int
    sender: Sender
    message: str

    def to_nonebot_reply(self) -> NonebotReply:
        model_dict = self.model_dump()
        message = model_dict.pop("message")
        message = Message(message)
        model_dict["message"] = message
        return NonebotReply(**model_dict)
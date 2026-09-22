from pydantic import BaseModel
from typing import Literal
from nonebot.adapters.onebot.v11.event import Sender, MessageEvent
from nonebot.adapters.onebot.v11.message import Message
from .reply import Reply

class MessageEventModel(BaseModel):
    post_type: Literal["message"]
    sub_type: str
    user_id: int
    message_type: str
    message_id: int
    message: str
    original_message: str
    raw_message: str
    font: int
    sender: Sender
    to_me: bool = False
    reply: Reply | None = None

    def to_message_event(self) -> MessageEvent:
        model_dict = self.model_dump()
        message = Message(model_dict.pop("message"))
        original_message = Message(model_dict.pop("original_message"))
        if self.reply is not None:
            reply = self.reply.to_nonebot_reply()
            model_dict["reply"] = reply
        model_dict["message"] = message
        model_dict["original_message"] = original_message
        
        return MessageEvent(**model_dict)
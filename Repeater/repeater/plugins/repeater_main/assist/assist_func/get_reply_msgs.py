from nonebot.adapters.onebot.v11 import Bot, MessageEvent, Message
from .get_message_event import get_message_event

async def get_reply_msgs(bot: Bot, message: Message) -> list[MessageEvent]:
    msgs: list[MessageEvent] = []
    for msg in message:
        if msg.type == "reply":
            msgs.append(
                await get_message_event(bot, msg.data["id"])
            )
    return msgs
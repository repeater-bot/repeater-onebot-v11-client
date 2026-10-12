from nonebot.adapters.onebot.v11 import Bot, Message, MessageEvent
from .make_message_event import make_message_event

async def get_forward_msgs(bot: Bot, message: Message) -> list[MessageEvent]:
    msgs: list[MessageEvent] = []

    for msg in message:
        if msg.type == "forward":
            forward_msg = await bot.get_forward_msg(id=msg.data["id"])
            messages = forward_msg["messages"]
            for sub_msg in messages:
                msgs.append(make_message_event(bot, sub_msg))
    return msgs
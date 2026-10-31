from nonebot.adapters.onebot.v11 import Bot, Message, MessageEvent
from .make_message_event import make_message_event

async def get_forward_msgs(
        bot: Bot,
        forward_msg_id: str,
    ) -> list[MessageEvent]:
    msgs: list[MessageEvent] = []
    
    forward_msg = await bot.get_forward_msg(id=forward_msg_id)
    messages = forward_msg["messages"]
    for sub_msg in messages:
        msgs.append(
            make_message_event(bot, sub_msg)
        )
    return msgs
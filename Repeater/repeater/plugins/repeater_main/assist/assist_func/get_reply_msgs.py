from nonebot.adapters.onebot.v11 import Bot, MessageEvent, Message
from .get_message_event import get_message_event
from .make_message_event import make_message_event

async def get_reply_msgs(bot: Bot, event: MessageEvent, args: Message) -> list[MessageEvent]:
    msgs: list[MessageEvent] = []
    if event.reply:
        message = event.reply.model_dump()
        return [make_message_event(bot, message)]
    else:
        if args:
            message = args
        else:
            message = event.message
            
        for msg in message:
            if msg.type == "reply":
                msgs.append(
                    await get_message_event(bot, msg.data["id"])
                )
        return msgs
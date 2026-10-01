from nonebot.adapters.onebot.v11 import Bot, MessageEvent
from .make_message_event import make_message_event
from ...logger import logger

async def get_message_event(bot: Bot, message_id: int) -> MessageEvent:
    response = await bot.get_msg(
        message_id = message_id
    )
    return make_message_event(bot, response)
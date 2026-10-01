from nonebot.adapters.onebot.v11 import Bot, MessageEvent
from .make_message_event import make_message_event
from ...logger import logger

async def get_group_message_history(
        bot: Bot,
        group_id: int,
        message_id: int = 0,
        count: int = 20,
        reverse_order: bool = False
    ) -> list[MessageEvent]:

    if reverse_order and message_id == 0:
        raise ValueError("reverse_order is True, but message_id is 0")
    
    response = await bot.get_group_msg_history(
        group_id = group_id,
        message_id = message_id,
        count = count,
        reverse = reverse_order
    )

    result = [
        make_message_event(bot, response)
        for response in response["messages"]
    ]

    return result

async def get_private_message_history(
        bot: Bot,
        user_id: int,
        message_id: int = 0,
        count: int = 20,
        reverse_order: bool = False
    ) -> list[MessageEvent]:

    if reverse_order and message_id == 0:
        raise ValueError("reverse_order is True, but message_id is 0")

    response = await bot.get_friend_msg_history(
        user_id = user_id,
        message_id = message_id,
        count = count,
        reverse = reverse_order
    )

    result = [
        make_message_event(bot, response)
        for response in response["messages"]
    ]

    return result
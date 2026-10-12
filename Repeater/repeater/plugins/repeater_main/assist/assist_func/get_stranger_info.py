from nonebot.adapters.onebot.v11 import Bot
from ..models import BusinessCard

async def get_stranger_info(
    bot: Bot,
    user_id: int,
    no_cache: bool = False
) -> BusinessCard:
    result = await bot.get_stranger_info(
        user_id = user_id,
        no_cache = no_cache
    )
    return BusinessCard(**result)
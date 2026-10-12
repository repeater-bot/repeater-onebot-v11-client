from nonebot.adapters.onebot.v11 import Bot
from ..models import GroupMemberInfo

async def get_group_member_info(
    bot: Bot,
    group_id: int,
    user_id: int,
    no_cache: bool = False,
) -> GroupMemberInfo:
    result = await bot.get_group_member_info(
        group_id = group_id,
        user_id = user_id,
        no_cache = no_cache,
    )
    return GroupMemberInfo(**result)
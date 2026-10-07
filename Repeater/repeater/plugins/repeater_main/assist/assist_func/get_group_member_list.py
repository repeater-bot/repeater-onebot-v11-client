from nonebot.adapters.onebot.v11 import Bot
from ..models import GroupMemberInfo

async def get_group_member_list(
    bot: Bot,
    group_id: int
) -> list[GroupMemberInfo]:
    result = await bot.get_group_member_list(
        group_id = group_id
    )
    return [
        GroupMemberInfo(**member)
        for member in result
    ]
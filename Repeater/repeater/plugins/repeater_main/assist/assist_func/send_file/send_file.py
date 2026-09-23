from nonebot.adapters.onebot.v11 import Bot, MessageEvent, Message
from ...namespace import MessageSource
from .send_group_file import send_group_file
from .send_private_file import send_private_file

async def send_file(
    bot: Bot,
    group_id: str,
    user_id: str,
    url: str,
    file_name: str,
    source: MessageSource,
) -> str | None:
    match source:
        case MessageSource.GROUP:
            return await send_group_file(
                bot,
                group_id,
                url,
                file_name,
            )
        case MessageSource.PRIVATE:
            return await send_private_file(
                bot,
                user_id,
                url,
                file_name,
            )
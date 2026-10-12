from nonebot.adapters.onebot.v11 import Bot, Message, MessageEvent
from typing import AsyncGenerator
from .get_reply_msgs import get_reply_msgs

async def get_reply_chain(
    bot: Bot,
    message: Message,
    max_depth: int | None = None
) -> AsyncGenerator[MessageEvent, None]:
    """
    获取回复链

    注：解析时，它会默认消息段中只有一个 reply 消息段，
    如果有存在多个，则使用第一个

    :param bot: Bot
    :param message: 消息
    :param max_depth: 最大深度
    """
    times: int = 0
    message_ids: set[int] = set()
    while True:
        if max_depth is not None and times >= max_depth:
            break
        
        reply_messages = await get_reply_msgs(
            bot = bot,
            message = message
        )
        if len(reply_messages) >= 1:
            event = reply_messages[0]
            yield event
            message = event.message
            if event.message_id in message_ids:
                break
            else:
                message_ids.add(event.message_id)
        else:
            break
        times += 1
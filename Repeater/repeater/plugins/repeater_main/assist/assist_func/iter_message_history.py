import asyncio
from typing import AsyncGenerator
from ..namespace import Namespace
from nonebot.adapters.onebot.v11 import Bot, MessageEvent
from .get_message_history import get_group_message_history, get_private_message_history

async def iter_message_history(
    bot: Bot,
    namespace: Namespace,
    iter_step: int = 100,
) -> AsyncGenerator[MessageEvent, None]:
    next_id: int = 0
    while True:
        if namespace.group_id and namespace.is_group:
            new_messages = await get_group_message_history(
                bot,
                group_id = int(namespace.group_id),
                message_id = next_id,
                count = iter_step + 1
            )
        elif namespace.user_id and namespace.is_private:
            new_messages = await get_private_message_history(
                bot,
                user_id = int(namespace.user_id),
                message_id = next_id,
                count = iter_step + 1
            )
        else:
            raise ValueError("Invalid namespace")

        next_id = new_messages[0].message_id
        messages = new_messages[:1:-1]  # Reverse the list

        for message in messages:
            yield message
            await asyncio.sleep(0) # Yield control back to the event loop
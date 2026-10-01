from nonebot.adapters.onebot.v11 import Bot, MessageEvent
from ...logger import logger

def make_message_event(bot: Bot, data: dict) -> MessageEvent:
    # 兼容 MessageEvent

    if "post_type" not in data:
        data["post_type"] = "message"
    elif data["post_type"] != "message":
        logger.warning(
            "get_message_event: post_type is {post_type}",
            post_type = data["post_type"]
        )
        data["post_type"] = "message"

    if "self_id" not in data:
        data["self_id"] = bot.self_id
    
    return MessageEvent(**data)
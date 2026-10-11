from nonebot.adapters.onebot.v11 import Message, MessageSegment

def is_empty_message(msg: str | Message | MessageSegment) -> bool:
    if isinstance(msg, str):
        return not bool(msg)
    elif isinstance(msg, Message):
        if len(msg) == 0:
            return True

        for seg in msg:
            if seg.type == "text":
                if seg.data["text"]:
                    return False
            elif seg.type not in ["at", "reply"]:
                return False
        return True
    elif isinstance(msg, MessageSegment):
        if msg.type == "text":
            if msg.data["text"]:
                return False
        elif msg.type not in ["at", "reply"]:
            return False
        return True
    else:
        raise TypeError(f"Invalid message type: {msg.__class__.__name__}")
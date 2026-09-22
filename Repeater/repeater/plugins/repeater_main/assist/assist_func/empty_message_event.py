from nonebot.adapters.onebot.v11 import MessageEvent, Message
from nonebot.adapters.onebot.v11.event import Reply, Sender

def make_empty_message_event() -> MessageEvent:
    empty_message_event = MessageEvent(
        time = 0,
        self_id = 0,
        post_type = "message",
        sub_type = "",
        user_id = 0,
        message_type = "",
        message_id = 0,
        message = Message(),
        original_message = Message(),
        raw_message = "",
        font = 0,
        sender = Sender(),
        to_me = False,
        reply = None,
    )
    return empty_message_event
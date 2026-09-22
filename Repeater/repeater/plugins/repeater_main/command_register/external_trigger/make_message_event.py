import time
from ...assist import Namespace, MessageSource
from nonebot.adapters.onebot.v11 import MessageEvent, Message, Bot
from nonebot.adapters.onebot.v11.event import Reply, Sender

def make_message_event(
    namespace: Namespace,
    self_id: int = 0,
    message_id: int = 0,
    message: Message = Message(),
    font: int = 0,
    nickname: str | None = None,
    sex: str | None = None,
    age: int | None = None,
    card: str | None = None,
    area: str | None = None,
    level: str | None = None,
    role: str | None = None,
    title: str | None = None,
    to_me: bool = False,
    sub_type: str = "normal",
) -> MessageEvent:
    empty_message_event = MessageEvent(
        time = time.time_ns() // 10**9,
        self_id = self_id,
        post_type = "message",
        sub_type = sub_type,
        user_id = int(namespace.user_id),
        message_type = namespace.mode.value,
        message_id = message_id,
        message = message,
        original_message = message,
        raw_message = str(message),
        font = font,
        sender = Sender(
            user_id = int(namespace.user_id),
            nickname = nickname,
            sex = sex,
            age = age,
            card = card,
            area = area,
            level = level,
            role = role,
            title = title
        ),
        to_me = to_me,
        reply = None,
        group_id = int(namespace.group_id) if namespace.mode == MessageSource.GROUP else None # type: ignore
    )
    return empty_message_event
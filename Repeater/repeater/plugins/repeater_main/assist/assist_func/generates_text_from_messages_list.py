from nonebot.adapters.onebot.v11 import MessageEvent
from typing import Iterable
from datetime import datetime
from pydantic import ValidationError

def generates_text_from_messages_list(messages: Iterable[dict | MessageEvent]):
    text_buffer: list[str] = []
    validation_failure_counter: int = 0
    for message in messages:
        if isinstance(message, MessageEvent):
            event = message
            nick_name = event.sender.card or event.sender.nickname
            text = event.message
            time = datetime.fromtimestamp(event.time)
        else:
            try:
                event = MessageEvent.model_validate(message)
            except ValidationError:
                try:
                    nick_name = message["sender"]["card"] or message["sender"]["nickname"]
                    text = message["message"]
                    time = datetime.fromtimestamp(message["time"])
                except KeyError:
                    validation_failure_counter += 1
                    continue
        
        time_str = time.strftime("%Y-%m-%d %H:%M:%S")
        text_buffer.append(
            f"[{time_str}]{nick_name}: {text}"
        )

    if validation_failure_counter > 0:
        text_buffer.append(f"Validation Failure: {validation_failure_counter}")
    return "\n".join(text_buffer)
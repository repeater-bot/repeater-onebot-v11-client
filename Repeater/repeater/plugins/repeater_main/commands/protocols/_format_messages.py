import re
from ...assist import PersonaInfo
from nonebot.adapters.onebot.v11 import Message, MessageSegment

def format_messages(message_history: list[PersonaInfo], pattern: re.Pattern) -> Message:
    message_buffer: Message = Message()
    for message in message_history:
        message_cqcode = message.message_cqcode
        if not pattern.match(message_cqcode):
            continue

        
        message_buffer.extend(
            obj = [
                MessageSegment.text(
                    text=f"{message.display_name}: [{message.time.isoformat()}|id:{message.message_id}]"
                ),
                *message.message
            ]
        )
    
    message_buffer.reduce()
    return message_buffer
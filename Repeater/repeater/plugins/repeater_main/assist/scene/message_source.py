from enum import StrEnum

class MessageSource(StrEnum):
    """
    消息来源
    """
    GROUP = "group"
    PRIVATE = "private"
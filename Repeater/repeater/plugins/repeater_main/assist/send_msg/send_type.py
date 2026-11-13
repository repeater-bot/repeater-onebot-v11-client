from enum import Enum, auto

class SendType(Enum):
    """
    发送处理类型
    """
    AUTO = auto()
    MATCHER = auto()
    API = auto()
    BUFFER = auto()
    NULL = auto()
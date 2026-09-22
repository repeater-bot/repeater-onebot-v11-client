from enum import Enum, auto

class EnterType(Enum):
    """
    PersonaInfo 进入方式
    """
    Command = auto()
    Message = auto()
    Horizontal = auto()
    External = auto()
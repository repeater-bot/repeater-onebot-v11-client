from enum import StrEnum

class UserdataCmdsType(StrEnum):
    """
    Userdata commands type
    """
    CONTEXT = "context"
    PROMPT= "prompt"
    CONFIG = "config"
    PROGRAM = "program"
    NONE = "none"
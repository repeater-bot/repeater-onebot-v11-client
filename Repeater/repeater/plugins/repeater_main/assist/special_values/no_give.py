from typing import Self, Any
from typing_extensions import TypeIs

class NoGive:
    """
    Use to distinguish default values for parameters that are not given.
    """
    _instance: Self | None = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

nogive = NoGive()

def is_no_give(value: Any | NoGive) -> TypeIs[NoGive]:
    # Compare addresses directly to speed up the comparison calculation, because the `NoGive` type is a global singleton.
    return value is nogive

def is_no_give_type(value: type[Any | NoGive]) -> TypeIs[type[NoGive]]:
    return type(value) is type and issubclass(value, NoGive)
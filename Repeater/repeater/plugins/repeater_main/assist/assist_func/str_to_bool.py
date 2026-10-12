from typing import overload, Literal

@overload
def str_to_bool(s: str) -> bool:
    ...

@overload
def str_to_bool(s: str, optional: Literal[True] = True) -> bool | None:
    ...

@overload
def str_to_bool(s: str, optional: Literal[False] = False) -> bool:
    ...

def str_to_bool(s: str, optional: bool = False) -> bool | None:
    """
    Convert a string to a boolean value.

    Parameters:
    s (str): The string to convert.

    Returns:
    bool: The boolean value of the string.
    """
    if optional and s.lower() in ["", "none", "null"]:
        return None
    if not isinstance(s, str):
        raise TypeError("Input must be a string.")
    if s.lower() in ["true", "yes", "1", "t", "y", "on"]:
        return True
    elif s.lower() in ["false", "no", "0", "f", "n", "off"]:
        return False
    else:
        raise ValueError(f"\"{s}\" cannot convert string to boolean.")
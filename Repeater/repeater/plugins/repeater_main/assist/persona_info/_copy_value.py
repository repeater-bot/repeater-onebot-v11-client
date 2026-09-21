from ..special_values import NoGive, is_no_give
from typing import Callable, TypeVar

T = TypeVar("T")

def copy_value(
        value: T | NoGive,
        get_new_value_deep: Callable[[], T],
        get_new_value_copy: Callable[[], T],
        get_new_value: Callable[[], T],
        copydata: bool = False,
        deepcopy: bool = False
    ) -> T:
    """
    复制值

    :param value: 值
    :param get_new_value_deep: 获取新值的函数，用于深复制
    :param get_new_value_copy: 获取新值的函数，用于浅复制
    :param get_new_value: 获取新值的函数，用于不复制
    :param copydata: 是否复制数据
    :param deepcopy: 是否深复制
    """
    new_value: T
    
    if is_no_give(value):
        if copydata:
            if deepcopy:
                new_value = get_new_value_deep()
            else:
                new_value = get_new_value_copy()
        else:
            new_value = get_new_value()
    else:
        new_value = value

    return new_value
from ...assist import escape_string
from ...command_register import CommandPackage, CommandCaller
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from typing import Type, Any

from ._split_by_indent import _strip_leading_text

def parse_input(message: list[list[Message]]) -> list[tuple[type[CommandPackage[Any]], Message]]:
    command_call: list[tuple[Type[CommandPackage[Any]], Message]] = []
    for index, line in enumerate(message, start=1):
        if not line:
            continue

        first_message = line[0]
        text = first_message.extract_plain_text()
        prefix, rest_text = split_cmd_prefix(text)
        if not prefix:
            raise ValueError(f"[{index}] {rest_text} is not a command")

        # 裁掉 "命令前缀 + 命令名 + 一个分隔空格"，其余部分（含非文本段）留给 args
        name = rest_text
        consumed = len(prefix) + len(rest_text)
        space_index = rest_text.find(" ")
        if space_index != -1:
            name = rest_text[:space_index]
            consumed = len(prefix) + space_index + 1

        args = _strip_leading_text(first_message, consumed)

        child_segments: list[MessageSegment] = [
            segment for msg in line[1:] for segment in msg
        ]
        if args and child_segments:
            # 行内参数与缩进子块之间补一个换行，否则首尾会粘成一个词
            args.append(MessageSegment.text("\n"))
        args.extend(child_segments)

        command_call.append(
            (
                CommandCaller.match_trigger(name),
                args
            )
        )

    return command_call

def split_cmd_prefix(name: str) -> tuple[str, str]:
    for prefix in CommandCaller.cmd_prefixs():
        if name.startswith(prefix):
            return prefix, name.removeprefix(prefix)

    return "", name
import asyncio
from typing import Any
from pydantic import ValidationError
from nonebot.adapters.onebot.v11 import MessageEvent
from collections import Counter
from ...assist import PersonaInfo, SendMsg, MessageSource, parse_delimited_string
from ...cmd_info import CmdTypes
from ...command_register import(
    CommandCaller,
    CommandPackage
)
from ...logger import logger

@CommandCaller.register
class HistoryCharStatistics(CommandPackage):
    cmd = "historyCharStatistics"
    aliases = {
        "hcs",
        "HCS",
        "history_char_statistics",
        "History_Char_Statistics",
        "HistoryCharStatistics",
        "HISTORY_CHAR_STATISTICS",
    }
    cmd_type = CmdTypes.OTHER
    acceptable_sources = {MessageSource.GROUP}
    description = f"""
    Statistics chat in the presence of the proportion of characters.

    Usage:
        /{cmd} message_count, top_count
    """

    @staticmethod
    def char_statistics(message_list: dict[str, Any], length: int | None = None) -> tuple[str, int, int]:
        messages: list[str] = []
        validation_failure_counter: int = 0
        total_effective: int = 0
        for message in message_list["messages"]:
            try:
                event = MessageEvent.model_validate(message)
                message_text = event.message.extract_plain_text()
                total_effective += 1
            except ValidationError:
                try:
                    message_text = "".join(seg["data"]["text"] for seg in message["message"] if seg["type"] == "text")
                    total_effective += 1
                except KeyError:
                    validation_failure_counter += 1
                    continue
            
            if not isinstance(message_text, str):
                logger.warning(
                    "member_name is not a string, it is {member_type}",
                    member_type = type(message_text).__name__,
                )
                continue
            
            messages.append(message_text)
        
        counter = Counter("".join(messages))
        char_count_list = list(counter.items())
        char_statistics_list = sorted(char_count_list, key=lambda x: x[1], reverse=True)

        text_list: list[str] = []
        for index, (name, count) in enumerate(char_statistics_list, start=1):
            if length and index >= length:
                break
            text_list.append(f"{index}. \"{name}\": {count}({count / counter.total():.2%})")
        text = "\n".join(text_list)

        return text, total_effective, validation_failure_counter

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        group_id = persona_info.group_id

        args = parse_delimited_string(persona_info.message_stripped_str)
        if len(args) != 2:
            await send_msg.send_error("Please enter two positive integers.")
            return
        message_count, length = args
        try:
            n = int(message_count)
        except (ValueError, TypeError):
            await send_msg.send_error("Please enter a valid number.")

        if n > 0:
            message_list = await persona_info.cached_api.get_group_msg_history(
                group_id = group_id,
                count = n
            )

            text, total_effective, validation_failure_counter = await asyncio.to_thread(
                self.char_statistics,
                message_list,
                int(length)
            )

            if validation_failure_counter > 0:
                await send_msg.send_warning(f"Warning: There are {validation_failure_counter} message verification failures.\n")
            await send_msg.send_check_length_prompt(text)
        else:
            await send_msg.send_error("The input must be a positive integer!")
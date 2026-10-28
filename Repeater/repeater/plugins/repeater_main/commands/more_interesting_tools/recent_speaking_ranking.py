import asyncio
from typing import Any
from pydantic import ValidationError
from nonebot.adapters.onebot.v11 import MessageEvent
from ...assist import PersonaInfo, SendMsg, MessageSource
from ...cmd_info import CmdTypes
from ...command_register import(
    CommandCaller,
    CommandPackage
)
from ...logger import logger

@CommandCaller.register
class RecentSpeakingRanking(CommandPackage):
    cmd = "recentSpeakingRanking"
    aliases = {
        "rsr",
        "RSR",
        "recent_speaking_ranking",
        "Recent_Speaking_Ranking",
        "RecentSpeakingRanking",
        "RECENT_SPEAKING_RANKING",
    }
    cmd_type = CmdTypes.OTHER
    acceptable_sources = {MessageSource.GROUP}

    @staticmethod
    def recent_speaking_ranking_worker(message_list: dict[str, Any]) -> tuple[str, int, int]:
        member_speech_count: dict[str, int] = {}
        validation_failure_counter: int = 0
        total_effective: int = 0
        for message in message_list["messages"]:
            try:
                event = MessageEvent.model_validate(message)
                member_name = event.sender.card or event.sender.nickname
                total_effective += 1
            except ValidationError:
                try:
                    member_name = message["sender"]["card"] or message["sender"]["nickname"]
                    total_effective += 1
                except KeyError:
                    validation_failure_counter += 1
                    continue
            if not isinstance(member_name, str):
                logger.warning(
                    "member_name is not a string, it is {member_type}",
                    member_type = type(member_name).__name__,
                )
                continue
            if member_name not in member_speech_count:
                member_speech_count[member_name] = 1
            else:
                member_speech_count[member_name] += 1

        member_speech_count_list = list(member_speech_count.items())
        sorted_member_speech_count_list = sorted(member_speech_count_list, key=lambda x: x[1], reverse=True)

        text_list: list[str] = []
        for index, (name, speech_count) in enumerate(sorted_member_speech_count_list, start=1):
            text_list.append(f"{index}. {name}: {speech_count}({speech_count / total_effective:.2%})")
        text = "\n".join(text_list)

        return text, total_effective, validation_failure_counter

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        group_id = persona_info.group_id

        try:
            n = int(persona_info.message_stripped_str)
        except (ValueError, TypeError):
            await send_msg.send_error("Please enter a valid number.")

        if n > 0:
            message_list = await persona_info.cached_api.get_group_msg_history(
                group_id=group_id,
                count=n
            )

            text, total_effective, validation_failure_counter = await asyncio.to_thread(
                self.recent_speaking_ranking_worker, message_list
            )

            if validation_failure_counter > 0:
                await send_msg.send_warning(f"Warning: There are {validation_failure_counter} message verification failures.\n")
            await send_msg.send_check_length_prompt(text)
        else:
            await send_msg.send_error("The input must be a positive integer!")
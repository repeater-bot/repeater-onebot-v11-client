from ...assist import PersonaInfo, SendMsg, MessageSource
from ...command_register import CommandCaller, ListenType
from .._bases import BaseChat, SendMessage
from ...client_configs import storage_configs
from typing import NoReturn

@CommandCaller.register
class CQChat(BaseChat):
    cmd = "CQChat"
    aliases = {
        "cqc",
        "CQC",
        "cqchat",
        "CQCHAT"
    }
    description = f"""
        Give the message to the AI using CQCode instead of parsing it.

        Usage:
        ```
        /{cmd} message
        ```
    """

    async def parse_message(
        self,
        persona_info: PersonaInfo,
        send_msg: SendMsg,
    ) -> SendMessage:
        if persona_info:
            if await super().enter_check(persona_info, send_msg):
                return await super().parse_message(persona_info, send_msg)
            else:
                send_msg.break_handler()
        else:
            await self.empty_message(persona_info, send_msg)

    async def empty_message(
        self,
        persona_info: PersonaInfo,
        send_msg: SendMsg
    ) -> NoReturn: 
        if persona_info.source == MessageSource.GROUP:
            await send_msg.send_hello()
        send_msg.break_handler()
from ...assist import PersonaInfo, SendMsg, MessageSource
from ...command_register import CommandCaller, ListenType
from .._bases import BaseChat, SendMessage
from ...client_configs import storage_configs
from typing import NoReturn

@CommandCaller.register
class SmartAT(BaseChat):
    listen_type = ListenType.Message
    priority = 100
    description = """
        Determines whether the input is null,
        to perform a build task,
        or output the specified text

        Usage:
        ```
        @Bot message
        ```

        Or:
        ```
        @Bot
        ```
    """

    async def enter_check(self, persona_info: PersonaInfo, send_msg: SendMsg) -> bool:
        return storage_configs.ignore_enter.allow_check_online

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
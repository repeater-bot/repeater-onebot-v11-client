import asyncio
from .objects.package import CommandPackage
from .objects.listen_type import ListenType
from .caller import CommandCaller
from ..cmd_info import CmdTypes
from ..assist import PersonaInfo, SendMsg, SendingTarget

@CommandCaller.register
class FrameworkMessageListener(CommandPackage):
    rule = None
    listen_type = ListenType.Message
    cmd_type = CmdTypes.LISTEN_ALL
    priority = 0
    block = False
    description = """
    A Handler inside the Repeater framework for unfiltered message listening.
    """

    async def enter_check(self, persona_info: PersonaInfo, send_msg: SendMsg) -> bool:
        send_msg.sending_target = SendingTarget.NULL
        return True

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        await CommandCaller.report_message(
            persona_info = persona_info,
            send_msg = send_msg,
            block_propagation = True
        )
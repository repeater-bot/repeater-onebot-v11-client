from ...assist import PersonaInfo, SendMsg
from ...command_register import CommandCaller, ListenType
from .._bases import BaseChat
from .smart_at import SmartAT

@CommandCaller.register
class SmartATCmd(BaseChat):
    cmd = "smartAT"
    aliases = {
        "smat",
        "SMAT",
        "smart_at",
        "Smart_AT",
        "SmartAT",
        "SMARTAT",
    }
    listen_type = ListenType.Command
    description = """
        The command version of SmartAT.

        Usage:
        ```
        @Bot message
        ```

        Or:
        ```
        @Bot
        ```
    """

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        return await CommandCaller.horizontal_call(
            package = SmartAT,
            persona_info = persona_info,
            send_msg = send_msg
        )
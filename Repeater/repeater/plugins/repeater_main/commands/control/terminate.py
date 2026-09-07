import asyncio

from ...assist import PersonaInfo, SendMsg
from ...cmd_info import CmdTypes
from ...command_register import(
    CommandCaller,
    CommandPackage
)

@CommandCaller.register
class Terminate(CommandPackage):
    cmd = "terminate"
    aliases = {
        "ter",
        "TER",
        "Terminate",
        "TERMINATE",
    }
    cmd_type = CmdTypes.CONTROL
    description = f"""
    Terminates execution of the entire command tree under the final parent node.

    Usage: 
    ```
    /{cmd} seconds
    ```
    """

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        send_msg.handler_finished()
import asyncio

from ...assist import PersonaInfo, SendMsg
from ...cmd_info import CmdTypes
from ...command_register import(
    CommandCaller,
    CommandPackage
)

@CommandCaller.register
class Poke(CommandPackage):
    cmd = "poke"
    aliases = {
        "Poke",
        "POKE",
    }
    cmd_type = CmdTypes.PROTOCOL
    description = f"""
    Send a poke message to the user.

    Usage: 
    ```
    /{cmd} @member
    ```
    """

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        at_list = persona_info.at_list
        if not at_list:
            await send_msg.send_poke()
        else:
            for member in at_list:
                await send_msg.send_poke(user_id = member)
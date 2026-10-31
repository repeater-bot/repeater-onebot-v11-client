import shlex
from ...assist import PersonaInfo, SendMsg
from ...cmd_info import CmdTypes
from ...command_register import(
    CommandCaller,
    CommandPackage
)

@CommandCaller.register
class SendFile(CommandPackage):
    cmd = "sendFile"
    aliases = {
        "sf",
        "SF",
        "send_file",
        "Send_File",
        "SendFile",
        "SEND_FILE"
    }
    cmd_type = CmdTypes.PROTOCOL
    description = f"""
    Send a file from url.
    *usage `shlex.split` to split the message.*

    Usage: 
    ```
    /{cmd} "url" "file_name"
    ```
    """

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        args = shlex.split(persona_info.message_stripped_str)
        if len(args) == 2:
            await send_msg.send_file(
                url = args[0],
                file_name = args[1]
            )
        elif len(args) > 2:
            await send_msg.send_text(
                "Too many arguments."
            )
        else:
            await send_msg.send_text(
                "Too few arguments."
            )
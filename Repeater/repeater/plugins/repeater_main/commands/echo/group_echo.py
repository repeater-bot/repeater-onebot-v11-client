from ...command_register import(
    CommandCaller,
    CommandPackage
)
from ...cmd_info import CmdTypes
from ...assist import PersonaInfo, SendMsg

@CommandCaller.register
class GroupEcho(CommandPackage):
    cmd = "groupEcho"
    aliases = {
        "gecho",
        "GECHO",
        "group_echo",
        "Group_Echo",
        "GroupEcho",
        "GRPUP_ECHO"
    }
    cmd_type = CmdTypes.ECHO
    description = f"""
    Echo a group message.
    If not arguments, echo the last message.

    Usage:
    ```
    /{cmd} [message]
    ```
    """

    # 定义一个主逻辑函数
    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):

        if not persona_info:
            await send_msg.send_prompt("Wait for input message...", continue_handler = True)
            new_message = await CommandCaller.wait_message(persona_info.scene)
            message = new_message.message
        else:
            message =  persona_info.message

        await send_msg.send_any(message, reply = False)
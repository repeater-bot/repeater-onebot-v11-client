import re
from ...command_register import(
    CommandCaller,
    CommandPackage
)
from ...cmd_info import CmdTypes
from ...assist import (
    PersonaInfo,
    SendMsg,
    Scene,
    MessageSource,
    SendingTarget
)

@CommandCaller.register
class RemoteEcho(CommandPackage):
    cmd = "remoteEcho"
    aliases = {
        "recho",
        "RECHO",
        "remote_echo",
        "Remote_Echo",
        "RemoteEcho",
        "REMOTE_ECHO"
    }
    cmd_type = CmdTypes.ECHO
    description = f"""
        Send the message somewhere else.
        
        Usage:
        ```
        /{cmd} group:<group_id> <message>
        /{cmd} private:<user_id> <message>
        ```
    """
    super_permissions = True

    pattern = re.compile(r"^(?P<mode>group|private)\s*:\s*(?P<id>\d+)\s*(?P<message>.+)$")

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        match = self.pattern.match(str(persona_info.message))
        if match:
            # 处理输入
            mode = match.group("mode")
            id = match.group("id")
            message_str = match.group("message")
            message = persona_info.make_message(message_str)
            match mode:
                case "group":
                    remote_send_msg = send_msg.copy(
                        target = Scene(
                            source = MessageSource.GROUP,
                            id = id,
                        ),
                        send_target = SendingTarget.API,
                    )
                case "private":
                    remote_send_msg = send_msg.copy(
                        target = Scene(
                            source = MessageSource.PRIVATE,
                            id = id,
                        ),
                        send_target = SendingTarget.API,
                    )
                case _:
                    await send_msg.send_prompt("Invalid mode, only 'group' or 'private' is allowed.")
                    send_msg.break_handler()
            remote_message = persona_info.copy(
                args = message,
            )
            if not remote_message:
                await send_msg.send_prompt("Waiting for message...", continue_handler = True)
                new_message = await CommandCaller.wait_message(persona_info.namespace)
                message = new_message.message
            else:
                message = remote_message.message

            await remote_send_msg.send_any(message, reply = False, continue_handler = True)
            await send_msg.send_prompt("Send successful.")
        else:
            await send_msg.send_prompt("Invalid format, please use 'group:<id> <message>' or 'private:<id> <message>'.")
            return
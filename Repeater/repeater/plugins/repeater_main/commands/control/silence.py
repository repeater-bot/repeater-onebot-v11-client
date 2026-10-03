from ...assist import PersonaInfo, SendMsg, SendingTarget
from ...cmd_info import CmdTypes
from ...command_register import(
    CommandCaller,
    CommandPackage
)
from ._peel_command import peel_command

@CommandCaller.register
class Silence(CommandPackage):
    cmd = "silence"
    aliases = {
        "sil",
        "SIL",
        "Silence",
        "SILENCE"
    }
    cmd_type = CmdTypes.CONTROL
    description = f"""
        Executes a command, but discards its output.

        Usage:
        ```
        /{cmd} command [args]
        ```
    """

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        peeled = peel_command(persona_info.message)
        if peeled is not None:
            command, args = peeled

            try:
                package = CommandCaller.match_trigger_or_component(command)
            except KeyError:
                await send_msg.send_error(f"Command {command} not found")
                return
            
            try:
                package_instance = CommandCaller.get_instance(package)
            except KeyError as e:
                await send_msg.send_error(f"Command {command} instance not found: {e}")
                return

            copyed_persona_info = persona_info.copy(
                args = args
            )
            copyed_send_msg = send_msg.copy(
                component = package_instance.component,
                send_target = SendingTarget.NULL
            )
            await CommandCaller.horizontal_call(
                package_instance,
                copyed_persona_info,
                copyed_send_msg
            )
        else:
            await send_msg.send_error("Invalid command format")
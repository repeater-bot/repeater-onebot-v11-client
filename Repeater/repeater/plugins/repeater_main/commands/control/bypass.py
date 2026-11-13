from ...assist import PersonaInfo, SendMsg, SendType
from ...cmd_info import CmdTypes
from ...command_register import(
    CommandCaller,
    CommandPackage
)
from ._peel_command import peel_command

@CommandCaller.register
class Bypass(CommandPackage):
    cmd = "bypass"
    aliases = {
        "byp",
        "BYP",
        "Bypass",
        "BYPASS"
    }
    cmd_type = CmdTypes.CONTROL
    description = f"""
        Run a command in the background,
        and quits immediately.

        Usage:
        ```
        /{cmd} command [args]
        ```
    """

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        peeled = peel_command(persona_info.message)
        if peeled is not None:
            components_or_trigger, args = peeled

            try:
                package = CommandCaller.match_trigger_or_component(components_or_trigger)
            except KeyError:
                await send_msg.send_error(f"Command {components_or_trigger} not found")
                return
            
            try:
                package_instance = CommandCaller.get_instance(package)
            except KeyError as e:
                await send_msg.send_error(f"Command instance {package.component} not found: {e}")
                return

            copied_persona_info = persona_info.copy(
                args = args
            )
            copied_send_msg = send_msg.copy(
                component = package_instance.component,
                send_target = SendType.API
            )
            await CommandCaller.horizontal_enter_wait_created(
                package_instance,
                copied_persona_info,
                copied_send_msg
            )
        else:
            await send_msg.send_error("Invalid command format")
from ...assist import PersonaInfo, SendMsg, SendingTarget
from ...cmd_info import CmdTypes
from ...command_register import(
    CommandCaller,
    CommandPackage
)
from ._peel_command import peel_command

@CommandCaller.register
class Asynchronously(CommandPackage):
    cmd = "asynchronously"
    aliases = {
        "async",
        "ASYNC",
        "Asynchronously",
        "ASYNCHRONOUSLY"
    }
    cmd_type = CmdTypes.CONTROL
    description = f"""
        Run a command in the background,
        and return the task id.


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

            copyed_persona_info = persona_info.copy(
                args = args
            )
            copyed_send_msg = send_msg.copy(
                component = package_instance.component,
                send_target = SendingTarget.API
            )
            package = await CommandCaller.horizontal_enter_wait_created(
                package_instance,
                copyed_persona_info,
                copyed_send_msg
            )
            await send_msg.send_text(str(package.task_id))
        else:
            await send_msg.send_error("Invalid command format")
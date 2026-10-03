from ...assist import PersonaInfo, SendMsg
from ...cmd_info import CmdTypes
from ...command_register import(
    CommandCaller,
    CommandPackage,
    SubCmdBreaked
)
from ._peel_command import peel_command

@CommandCaller.register
class ReverseResult(CommandPackage):
    cmd = "flipResult"
    aliases = {
        "fr",
        "FR",
        "flip_result",
        "Flip_Result",
        "FlipResult",
        "FLIP_RESULT",
    }
    cmd_type = CmdTypes.CONTROL
    description = f"""
    Flip the results of the execution
    Returns 1 when the execution result is 0
    Returns 0 if the execution result is not 0

    Usage: 
    ```
    /{cmd} command args
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
                component = package_instance.component
            )

            result = await CommandCaller.horizontal_call(
                package_instance,
                copyed_persona_info,
                copyed_send_msg
            )

            if isinstance(result, SubCmdBreaked):
                if result.code == 0:
                    send_msg.break_handler(1)
                else:
                    send_msg.break_handler(0)
            else:
                send_msg.break_handler(1)
        else:
            await send_msg.send_error("Invalid command format")
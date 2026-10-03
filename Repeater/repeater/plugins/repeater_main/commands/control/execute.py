from ...assist import PersonaInfo, SendMsg
from ...cmd_info import CmdTypes
from ...command_register import(
    CommandCaller,
    CommandPackage
)
from ._peel_command import peel_command

@CommandCaller.register
class Execute(CommandPackage):
    cmd = "execute"
    aliases = {
        "e",
        "E",
        "Execute",
        "EXECUTE"
    }
    cmd_type = CmdTypes.CONTROL
    description = f"""
        Pull Up the command invocation through component when only the component of the command are known.

        Usage:
        ```
        /{cmd} component [args] 
        ```
    """

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        peeled = peel_command(persona_info.message)
        if peeled is not None:
            components, args = peeled

            try:
                package = CommandCaller.match_component(components)
            except KeyError:
                await send_msg.send_error(f"Command {components} not found")
                return
            
            try:
                package_instance = CommandCaller.get_instance(package)
            except KeyError as e:
                await send_msg.send_error(f"Command {components} instance not found: {e}")
                return

            copyed_persona_info = persona_info.copy(
                args = args
            )
            copyed_send_msg = send_msg.copy(
                component = package_instance.component
            )
            await CommandCaller.horizontal_call(
                package_instance,
                copyed_persona_info,
                copyed_send_msg
            )
        else:
            await send_msg.send_error("Invalid command format")
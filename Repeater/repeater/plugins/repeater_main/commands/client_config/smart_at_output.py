from ...assist import PersonaInfo, SendMsg, str_to_bool
from ...cmd_info import CmdTypes
from ...command_register import(
    CommandCaller,
    CommandPackage
)

@CommandCaller.register
class SmartATOutput(CommandPackage):
    cmd = "smartATOutput"
    aliases = {
        "sato",
        "SATO",
        "smart_at_output",
        "SmartAT_Output",
        "SmartATOutput",
        "SMARTAT_OUTPUT",
    }
    description = f"""
        Turn the output of SmartAT on or off.

        Usage:
        ```
        /{cmd} true
        ```
        or
        ```
        /{cmd} false
        ```
    """
    cmd_type = CmdTypes.CLIENT_CONFIG

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        user_configs = await persona_info.get_user_configs()
        user_configs.smart_at_output = str_to_bool(persona_info.message_stripped_str)
        await persona_info.set_user_configs(user_configs)

        if user_configs.smart_at_output:
            await send_msg.send_prompt(
                "Turn on SmartAT's output."
            )
        else:
            await send_msg.send_prompt(
                "Turn off SmartAT's output."
            )
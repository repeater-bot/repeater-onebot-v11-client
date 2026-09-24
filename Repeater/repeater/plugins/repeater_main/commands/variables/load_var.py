import re
from ...assist import (
    PersonaInfo,
    SendMsg,
    Variables
)
from ...command_register import(
    CommandCaller,
    CommandPackage
)
from ...cmd_info import CmdTypes

@CommandCaller.register
class LoadVar(CommandPackage):
    cmd = "loadVar"
    aliases = {
        "lv",
        "LV",
        "load_var",
        "Load_Var",
        "LoadVar",
        "LOAD_VAR",
    }
    cmd_type = CmdTypes.VARIABLE
    description = f"""
    Load variables from user configs.

    Usage:
    ```
    /{cmd}
    ```
    """

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        user_configs = await persona_info.get_user_configs()
        if user_configs.variables is None:
            await send_msg.send_error("No variables found.")
        else:
            async with CommandCaller.variable_lock:
                variables = CommandCaller.variables.get(persona_info.namespace)
                if variables is None:
                    variables = Variables()
                    CommandCaller.variables[persona_info.namespace] = variables

                variables.load(user_configs, persona_info.message_stripped_str)
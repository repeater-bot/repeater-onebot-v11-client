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
class SetVar(CommandPackage):
    cmd = "setVar"
    aliases = {
        "sv",
        "SV",
        "set_var",
        "Set_Var",
        "SetVar",
        "SET_VAR",
    }
    cmd_type = CmdTypes.VARIABLE
    description = f"""
    Set a variable.

    Usage:
    ```
    /{cmd} <var_name>=<var_value>
    ```
    """

    pattern = re.compile(r"^\s*(?P<name>[\w\d_]+)\s*=\s*(?P<value>.+)\s*$")

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        match_result = self.pattern.match(persona_info.message_cqcode)
        if match_result:
            name = match_result.group("name")
            value = match_result.group("value")

            assert isinstance(name, str), f"name must be str, but got {type(name).__name__}"
            assert isinstance(value, str), f"value must be str, but got {type(value).__name__}"

            async with CommandCaller.variable_lock:
                variables = CommandCaller.variables.setdefault(persona_info.namespace, Variables())
                variables[name] = value

            await send_msg.send_prompt("Variable set successfully.")
        else:
            await send_msg.send_error("Invalid syntax.")
        
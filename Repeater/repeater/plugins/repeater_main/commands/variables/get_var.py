from ...assist import (
    PersonaInfo,
    SendMsg
)
from ...command_register import(
    CommandCaller,
    CommandPackage
)
from ...cmd_info import CmdTypes

@CommandCaller.register
class GetVar(CommandPackage):
    cmd = "getVar"
    aliases = {
        "gv",
        "GV",
        "get_var",
        "Get_Var",
        "GetVar",
        "GET_VAR",
    }
    cmd_type = CmdTypes.VARIABLE
    description = f"""
    Get a variable.

    Usage:
    ```
    /{cmd} <var_name>
    ```
    """

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        async with CommandCaller.variable_lock:
            variables = CommandCaller.variables.get(persona_info.namespace)

            if variables is None:
                await send_msg.send_error("No variables found, maybe you should create one first.")
                return

            var_name = persona_info.message_stripped_str
            if var_name in variables:
                var_value = variables.get(var_name)
                if var_value is None:
                    await send_msg.send_error("No variable found.")
                    send_msg.break_handler()
                message = persona_info.make_message(var_value)
                await send_msg.send_any(message, reply = False)
            else:
                await send_msg.send_error(f"Variable \"{var_name}\" not found.")
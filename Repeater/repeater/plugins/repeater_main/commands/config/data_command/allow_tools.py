import json
from ....assist import PersonaInfo, SendMsg, Response, parse_delimited_string
from ....command_register import CommandCaller
from ..._bases import BaseConfig, OperationType

@CommandCaller.register
class AllowTools(BaseConfig):
    cmd = "allowTools"
    aliases= {
        "at",
        "AT",
        "allow_tools",
        "Allow_Tools",
        "AllowTools",
        "ALLOW_TOOLS",
    }
    field = "allowed_tool_calls"
    operation = OperationType.GET_AND_SET
    description = f"""
    Add an allowed tool calls.

    Usage:
      /{cmd} tool_id [tool_id...]
    """

    async def parse_value(
        self,
        persona_info: PersonaInfo,
        send_msg: SendMsg,
        raw_value: list[str] | None = None
    ):
        if raw_value is None:
            tools = set()
        else:
            tools = set(raw_value)
        msg = persona_info.message_stripped_str
        add_tools = parse_delimited_string(msg)
        for tool in add_tools:
            if tool not in tools:
                tools.add(tool)
        return list(tools)
    
    async def finish_message(
            self,
            persona_info: PersonaInfo,
            send_msg: SendMsg,
            response: Response,
            field: str,
            value: list[str] | None
        ):
            await send_msg.send_response_check_code(response, f"Set Tool Calls to {json.dumps(value, ensure_ascii = False)}")
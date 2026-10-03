import re
import json
from ....assist import PersonaInfo, SendMsg, Response
from ....command_register import CommandCaller
from ..._bases import BaseConfig, OperationType

@CommandCaller.register
class AddPresetDirectives(BaseConfig):
    cmd = "addPresetDirectives"
    aliases= {
        "apd",
        "APD",
        "add_preset_directives",
        "Add_Preset_Directives",
        "AddPresetDirectives",
        "ADD_PRESET_DIRECTIVES",
    }
    field = "prompt_directives"
    operation = OperationType.GET_AND_SET
    description = f"""
    Add a preset directive to the config file.

    Usage:
      /{cmd} name:value
    """
    _pattern = re.compile(r"^(?P<name>\S+)\s*:\s*(?P<value>.*)$", re.DOTALL)

    @classmethod
    def parse_input(
        cls,
        text: str
    ):
        match = cls._pattern.match(text)
        if match is None:
            return None
        else:
            name = match.group("name")
            value = match.group("value")
            
            assert isinstance(name, str), "name must be a string"
            assert isinstance(value, str), "value must be a string"

            return {
                name: value
            }

    async def parse_value(
        self,
        persona_info: PersonaInfo,
        send_msg: SendMsg,
        raw_value: dict[str, list[str]] | None = None
    ):
        if raw_value is None:
            raw_value = {}
        msg = persona_info.message_stripped_str
        update_directives = self.parse_input(msg)
        if update_directives is None:
            await send_msg.send_error("Invalid input format. Expected: <name>: <value>...")
            send_msg.break_handler()
        for name, value in update_directives.items():
            if name in raw_value:
                if not value in raw_value[name]:
                    raw_value[name].append(value)
            else:
                raw_value[name] = [value]
        return raw_value
    
    async def finish_message(
            self,
            persona_info: PersonaInfo,
            send_msg: SendMsg,
            response: Response,
            field: str,
            value: list[str] | None
        ):
            await send_msg.send_response_check_code(response, f"Added Preset Directives to {json.dumps(value, ensure_ascii = False)}")
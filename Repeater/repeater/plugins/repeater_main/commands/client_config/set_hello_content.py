import orjson
import yaml

from ...assist import PersonaInfo, SendMsg
from ...cmd_info import CmdTypes
from ...command_register import(
    CommandCaller,
    CommandPackage
)
from ...client_configs import storage_configs, HelloContent
from pydantic import ValidationError

@CommandCaller.register
class SetHelloContent(CommandPackage):
    cmd = "setHelloContent"
    aliases = {
        "shc",
        "SHC",
        "set_hello_content",
        "Set_Hello_Content",
        "SetHelloContent",
        "SET_HELLO_CONTENT",
    }
    description = f"""
        Set the hello content.

        Usage:
        ```
        /{cmd} hello_content_setting
        ```
    """
    cmd_type = CmdTypes.CLIENT_CONFIG

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        user_configs = await persona_info.get_user_configs()
        hello_content = persona_info.message_stripped_str
        try:
            data = orjson.loads(hello_content)
        except orjson.JSONDecodeError:
            try:
                data = yaml.safe_load(hello_content)
            except yaml.YAMLError:
                await send_msg("Invalid JSON or YAML format.")
                return
        
        if data is None:
            user_configs.hello_content = None
        elif not isinstance(data, dict):
            await send_msg("Invalid JSON or YAML format.")
            return
        else:
            try:
                user_configs.hello_content = HelloContent.model_validate(data)
            except ValidationError as e:
                errors = e.errors()
                buffer: list[str] = []
                for error in errors:
                    buffer.append(f"{'.'.join(str(i) for i in error['loc'])}: {error['msg']}")
                await send_msg.send_error(
                    f"Invalid hello content setting:\n{''.join(buffer)}"
                )
        await persona_info.set_user_configs(user_configs)
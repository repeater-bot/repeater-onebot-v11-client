from ...assist import PersonaInfo, SendMsg, parse_delimited_string
from ...client_configs import ChatOutputMode
from ...cmd_info import CmdTypes
from ...command_register import(
    CommandCaller,
    CommandPackage
)

@CommandCaller.register
class ChatOutput(CommandPackage):
    cmd = "chatOutput"
    aliases = {
        "co",
        "CO",
        "chat_output",
        "Chat_Output",
        "ChartOutput",
        "CHAT_OUTPUT",
    }
    description = f"""
        Set the output mode of Chat Command.

        Usage:
        ```
        /{cmd} image,image,auto
        ```
        The first value is the output pattern of the inference content.
        The second value is the output pattern of the tool call.
        The third value is the output mode of the body.

        Valid values:
        - image: Render the output as markdown image.
        - text: Output text directly.
        - auto: Automatically choose the best mode.
        - null: Disable the output.
        - default: Use the default value.
    """
    cmd_type = CmdTypes.CLIENT_CONFIG

    def parse_value(self, value: str) -> ChatOutputMode | None:
        match value.lower():
            case "image":
                return ChatOutputMode.IMAGE
            case "text":
                return ChatOutputMode.TEXT
            case "auto":
                return ChatOutputMode.AUTO
            case "null":
                return ChatOutputMode.NULL
            case "default":
                return None
            case _:
                raise ValueError(f"Invalid value: {value}")

    def format_value(self, value: ChatOutputMode | None) -> str:
        if isinstance(value, ChatOutputMode):
            return value.value
        elif value is None:
            return "default"
        else:
            raise ValueError(f"Invalid value: {value}")

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        user_configs = await persona_info.get_user_configs()
        text = persona_info.message_stripped_str
        texts = parse_delimited_string(text)
        if len(texts) > 3:
            return await send_msg.send_error("Invalid arguments.")
        elif len(texts) < 3:
            return await send_msg.send_error("Not enough arguments.")
        else:
            (
                reasoning_content_mode,
                tool_content_mode,
                content_mode,
            ) = (
                self.parse_value(texts[0]),
                self.parse_value(texts[1]),
                self.parse_value(texts[2]),
            )
            user_configs.chat_output.reasoning_content = reasoning_content_mode
            user_configs.chat_output.tool_content = tool_content_mode
            user_configs.chat_output.content = content_mode
            await persona_info.set_user_configs(user_configs)
            await send_msg.send_prompt(
                prompt = "\n".join([
                    "Set chat output to:",
                    f"Reasoning Content: {self.format_value(value=reasoning_content_mode)}",
                    f"Tool Content: {self.format_value(value=tool_content_mode)}",
                    f"Content: {self.format_value(value=content_mode)}"
                ])
            )
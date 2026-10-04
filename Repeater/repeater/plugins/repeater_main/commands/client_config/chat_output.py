from ...assist import PersonaInfo, SendMsg, ChatOutputMode
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
        Turn the output mode of Chat Command.

        Usage:
        ```
        /{cmd} auto
        ```
        or
        ```
        /{cmd} text
        ```
        or
        ```
        /{cmd} image
        ```
        or
        ```
        /{cmd} null
        ```
    """
    cmd_type = CmdTypes.CLIENT_CONFIG

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        user_configs = await persona_info.get_user_configs()
        text = persona_info.message_stripped_str
        try:
            user_configs.chat_output = ChatOutputMode(text.lower())
        except ValueError:
            await send_msg.send_error(
                f"{text} is Invalid Chat Output Mode."
            )
            return
        await persona_info.set_user_configs(user_configs)

        if user_configs.chat_output:
            await send_msg.send_prompt(
                "Turn on SmartAT's output."
            )
        else:
            await send_msg.send_prompt(
                "Turn off SmartAT's output."
            )
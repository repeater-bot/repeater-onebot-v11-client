import re
import asyncio

from ...assist import PersonaInfo, SendMsg
from ...cmd_info import CmdTypes
from ...command_register import(
    CommandCaller,
    CommandPackage
)
from .serial import Serial

@CommandCaller.register
class TextTrigger(CommandPackage):
    cmd = "textTrigger"
    aliases = {
        "tt",
        "TT",
        "text_trigger",
        "Text_Trigger",
        "TextTrigger",
        "TEXT_TRIGGER"
    }
    cmd_type = CmdTypes.CONTROL
    description = f"""
        The first non-null behavior fires the regular expression.
        The partial sequential execution of the regular expression when triggered.

        Usage:
        ```
        /{cmd} .*
        /command 1
        /command 2
        ...
        ```
    """

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg) -> None:
        lines = persona_info.message_stripped_str.split("\n", 1)
        if not lines:
            return
        regex = lines[0]
        commands = lines[1]
        try:
            pattern = re.compile(regex)
        except re.error as e:
            await send_msg.send_error(f"Invalid regex: {e}")
            return

        while True:
            new_message = await CommandCaller.wait_message(persona_info.namespace)

            if not asyncio.to_thread(pattern.match, new_message.message_stripped_str):
                continue

            if commands:
                new_commands = new_message.copy(
                    args = new_message.make_message(
                        message = commands.replace(
                            "{message}", new_message.message_cqcode
                        )
                    )
                )

            copyed_send_msg = send_msg.copy(
                persona_info = new_commands,
                reply = persona_info.reply,
            )

            await CommandCaller.horizontal_call(
                Serial,
                persona_info = new_commands,
                send_msg = copyed_send_msg
            )
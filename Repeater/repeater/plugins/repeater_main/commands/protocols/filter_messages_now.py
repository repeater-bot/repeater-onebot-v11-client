import re

from ...assist import PersonaInfo, SendMsg, MessageSource
from ...cmd_info import CmdTypes
from ...command_register import(
    CommandCaller,
    CommandPackage
)
from ._format_messages import format_messages

@CommandCaller.register
class FilterMessagesNow(CommandPackage):
    cmd = "filterMessagesNow"
    aliases = {
        "fmn",
        "FMN",
        "filter_messages_now",
        "Filter_Messages_Now",
        "FilterMessagesNow",
        "FILTER_MESSAGES_NOW",
    }
    cmd_type = CmdTypes.PROTOCOL
    description = f"""
    Use regular expression to filter out the desired content from the history messages,
    and use the current environment.

    Usage: 
    ```
    /{cmd} message_id:count regex
    ```
    """

    pattern = re.compile(r"^(?P<message_id>\S*)\s*:\s*(?P<count>\d+)\s+(?P<regex>.+)$", re.IGNORECASE | re.DOTALL)

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        message_input = persona_info.message_stripped_str
        match_result = self.pattern.match(message_input)
        if match_result:
            message_id_str = match_result.group("message_id")
            count_str = match_result.group("count")
            regex = match_result.group("regex")

            assert isinstance(message_id_str, str), "message_id must be str"
            assert isinstance(count_str, str), "count_str must be str"
            assert isinstance(regex, str), "regex must be str"

            source = persona_info.source
            match source:
                case MessageSource.GROUP:
                    id = persona_info.group_id
                    if not id:
                        await send_msg.send_error("No group_id found")
                        return
                case MessageSource.PRIVATE:
                    id = persona_info.user_id
                case _:
                    await send_msg.send_error("Unsupported source")
                    return

            message_id = int(message_id_str) if message_id_str else 0
            count = int(count_str) if count_str else 20
            if count > 0:
                reverse_order = False
            elif count < 0:
                reverse_order = True
                count = -count
            else:
                raise ValueError("count must not be 0")
            
            pattern = re.compile(regex)

            message_history = await persona_info.from_message_history(
                source,
                id,
                message_id = message_id,
                count = count,
                reverse_order = reverse_order,
            )
            message = format_messages(message_history, pattern)

            await send_msg.send_check_length(
                message,
            )
        else:
            await send_msg.send_error("Invalid argument format")
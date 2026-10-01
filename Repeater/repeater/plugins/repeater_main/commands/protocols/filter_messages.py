import re

from ...assist import PersonaInfo, SendMsg, MessageSource
from ...cmd_info import CmdTypes
from ...command_register import(
    CommandCaller,
    CommandPackage
)
from ._format_messages import format_messages

@CommandCaller.register
class FilterMessages(CommandPackage):
    cmd = "filterMessages"
    aliases = {
        "fm",
        "FM",
        "filter_messages",
        "Filter_Messages",
        "FilterMessages",
        "FILTER_MESSAGES",
    }
    cmd_type = CmdTypes.PROTOCOL
    description = f"""
    Use regular expression to filter out the desired content from the history messages

    Usage: 
    ```
    /{cmd} group/private:id message_id:count regex
    ```
    """
    super_permission = True

    pattern = re.compile(r"^(?P<group_or_private>group|private)\s*:\s*(?P<id>\S+?)\s*(?P<message_id>\S*)\s*:\s*(?P<count>\d+)\s+(?P<regex>.+)$", re.IGNORECASE | re.DOTALL)

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        message_input = persona_info.message_stripped_str
        match_result = self.pattern.match(message_input)
        if match_result:
            group_or_private = match_result.group("group_or_private")
            id = match_result.group("id")
            message_id_str = match_result.group("message_id")
            count_str = match_result.group("count")
            regex = match_result.group("regex")

            assert isinstance(group_or_private, str), "group_or_private must be str"
            assert isinstance(id, str), "id must be str"
            assert isinstance(message_id_str, str), "message_id must be str"
            assert isinstance(count_str, str), "count_str must be str"
            assert isinstance(regex, str), "regex must be str"

            try:
                source = MessageSource(group_or_private)
            except ValueError:
                await send_msg.send_error("source must be group or user")
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
import re

from ...assist import PersonaInfo, SendMsg, Namespace
from ...cmd_info import CmdTypes
from ...command_register import(
    CommandCaller,
    CommandPackage
)

@CommandCaller.register
class FilterMessages(CommandPackage):
    cmd = "filterMessages"
    aliases = {
        "fltmsg",
        "FLTMSG",
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
    /{cmd} namespace message_id:count regex
    ```
    """

    pattern = re.compile(r"^(?P<namespace>\S+)\s+(?P<message_id>\S+)\s*:\s*(?P<count>\d+)\s+(?P<regex>.+)$")

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        message_input = persona_info.message_stripped_str
        match_result = self.pattern.match(message_input)
        if match_result:
            namespace_str = match_result.group("namespace")
            message_id_str = match_result.group("message_id")
            count_str = match_result.group("count")
            regex = match_result.group("regex")

            assert isinstance(namespace_str, str), "namespace must be str"
            assert isinstance(message_id_str, str), "message_id must be str"
            assert isinstance(count_str, str), "count_str must be str"
            assert isinstance(regex, str), "regex must be str"

            try:
                namespace = Namespace.from_str(namespace_str)
            except ValueError:
                await send_msg.send_text(f"Invalid namespace: {namespace_str}")
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
                message_id = message_id,
                count = count,
                reverse_order = reverse_order,
            )
            text_buffer: list[str] = []
            for message in message_history:
                message_cqcode = message.message_cqcode
                if not pattern.match(message_cqcode):
                    continue

                text_buffer.append(
                    f"{message.display_name}: [{message.time.isoformat()}|id:{message.message_id}]"
                )
                text_buffer.append(
                    message.message_cqcode
                )

            message = persona_info.make_message("\n".join(text_buffer))
            message.reduce()

            await send_msg.send_check_length(
                message,
            )
        else:
            await send_msg.send_error("Invalid argument format")
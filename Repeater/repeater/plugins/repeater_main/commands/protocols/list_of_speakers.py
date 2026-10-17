import asyncio

from datetime import timedelta
from ...assist import PersonaInfo, SendMsg
from ...cmd_info import CmdTypes
from ...command_register import(
    CommandCaller,
    CommandPackage
)

@CommandCaller.register
class ListOfSpeakers(CommandPackage):
    cmd = "listOfSpeakers"
    aliases = {
        "los",
        "LOS",
        "list_of_speakers",
        "List_Of_Speakers",
        "ListOfSpeakers",
        "LIST_OF_SPEAKERS"
    }
    cmd_type = CmdTypes.PROTOCOL
    description = f"""
    List of speakers at designated time in today.

    Usage: 
    ```
    /{cmd}
    ```
    """

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        count: dict[str, int] = {}
        total_count: int = 0
        async for history in persona_info.from_iter_message_history():
            if history.time.date() >= (persona_info.time.date() - timedelta(days=1)):
                id = f"{history.display_name}({history.user_id})"
                if id in count:
                    count[id] += 1
                else:
                    count[id] = 1
                total_count += 1
            else:
                break
        counts = await asyncio.to_thread(sorted, count.items(), key=lambda x: x[1], reverse=True)
        text_buffer = [f"{i[0]}: {i[1]}" for i in counts]
        await send_msg.send_check_length_prompt(f"Total: {total_count}\n" + "\n".join(text_buffer))
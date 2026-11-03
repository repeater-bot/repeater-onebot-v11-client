from ...assist import PersonaInfo, SendMsg
from ...cmd_info import CmdTypes
from ...command_register import(
    CommandCaller,
    CommandPackage
)
from ...clients import ChatClient

@CommandCaller.register
class BreakChatTask(CommandPackage):
    cmd = "breakChatTask"
    aliases = {
        "bct",
        "BCT",
        "break_chat_task",
        "Break_Chat_Task",
        "BreakChatTask",
        "BREAK_CHAT_TASK",
    }
    cmd_type = CmdTypes.STATUS
    description = f"""
    Break a chat task.

    Usage:
    ```
    /{cmd} [task_id]
    ```
    """

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        task_id = persona_info.message_stripped_str
        user_configs = await persona_info.get_user_configs()
        client = ChatClient(persona_info, user_configs)
        response = await client.break_chat_task(task_id if task_id else None)
        if response:
            break_response = response.get_data()
            if break_response is None:
                await send_msg.send_error("Failed parsing response data.")
            else:
                await send_msg.send_prompt(break_response.msg)
        else:
            await send_msg.send_error_response(response)
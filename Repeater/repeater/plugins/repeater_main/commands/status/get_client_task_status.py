from typing import Any
from ...assist import PersonaInfo, SendMsg
from ...cmd_info import CmdTypes
from ...command_register import(
    CommandCaller,
    CommandPackage
)
from ...clients import StatusClient


@CommandCaller.register
class GetCoreTaskStatus(CommandPackage):
    cmd = "getCoreTaskStatus"
    aliases = {
        "gcts",
        "GCTS",
        "get_client_task_status",
        "Get_Client_Task_Status",
        "GetCoreTaskStatus",
        "GET_CORE_TASK_STATUS",
    }
    cmd_type = CmdTypes.STATUS
    description = f"""
    Gets the status of the current LLM Text Content Generation Task.

    Usage:
    ```
    /{cmd}
    ```
    """

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        user_configs = await persona_info.get_user_configs()
        status_client = StatusClient(persona_info, user_configs)
        response = await status_client.get_client_task_status(persona_info.namespace_str)
        if response:
            status_response = response.get_data()
            if not status_response:
                await send_msg.send_prompt("Free")
            else:
                text_buffer: list[str] = []
                for task_id, task in status_response.tasks.items():
                    text_buffer.append(task_id)
                    for index, status in enumerate(task):
                        if index == 0:
                            prefix = ""
                        else:
                            prefix = ("  " * index) + "└ "
                        text_buffer.append(prefix + status)

                await send_msg.send_check_length_prompt("\n".join(text_buffer))
        else:
            await send_msg.send_response_check_code(response)
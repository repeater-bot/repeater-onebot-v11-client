import uuid
from ...assist import PersonaInfo, SendMsg
from ...cmd_info import CmdTypes
from ...command_register import(
    CommandCaller,
    CommandPackage
)
from ...logger import logger

@CommandCaller.register
class Wait(CommandPackage):
    cmd = "wait"
    aliases = {
        "wt",
        "WT",
        "Wait",
        "WAIT",
    }
    cmd_type = CmdTypes.CONTROL
    description = f"""
    Wait a task to finish.

    Usage: 
    ```
    /{cmd} task_id
    ```
    """

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        try:
            task_id = uuid.UUID(persona_info.message_stripped_str)
        except ValueError:
            await send_msg("Invalid task id.")

        if await CommandCaller.has_running_task(persona_info.namespace, task_id):
            async with CommandCaller.running_lock:
                task = CommandCaller.runnings.get(task_id)
                if task is None:
                    await send_msg.send_error("This task exists in the user runtime list, but not in the global runtime list.")
                else:
                    component = task.package.component
                    logger.info(
                        "Wait task {task_id}({component})",
                        task_id = task_id,
                        component = component
                    )
                    return await task
        else:
            await send_msg.send_error("Task not found.")
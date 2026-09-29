import time
from datetime import datetime
from typing import Any
from ...assist import PersonaInfo, SendMsg, format_time_duration_ns
from ...cmd_info import CmdTypes
from ...command_register import(
    CommandCaller,
    CommandPackage,
    RunningPackage
)

@CommandCaller.register
class TaskList(CommandPackage):
    cmd = "taskList"
    aliases = {
        "tl",
        "TL",
        "task_list",
        "TaskList",
        "Tast_List",
        "TASK_LIST",
    }
    cmd_type = CmdTypes.CONTROL
    description = f"""
    Show all tasks.

    Usage: 
    ```
    /{cmd}
    ```
    """

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        tasks_set = await CommandCaller.get_runnings(persona_info.namespace)
        now_monotonic_time = time.perf_counter_ns()
        if tasks_set:
            tasks_map: dict[str, list[RunningPackage[Any]]] = {}
            for task in tasks_set:
                if task.package.component not in tasks_map:
                    tasks_map[task.package.component] = []
                tasks_map[task.package.component].append(task)

            text_buffer: list[str] = []
            for component, tasks in tasks_map.items():
                text_buffer.append(f"[{component}]")
                for index, task in enumerate(tasks):
                    task_id = task.task_id
                    start_formatted = datetime.fromtimestamp(task.start_time / 1e9).isoformat()
                    formatted_running_time_ms = f"{(now_monotonic_time - task.start_monotonic_time) / 1e6:.3f}"
                    formatted_running_time = format_time_duration_ns(now_monotonic_time - task.start_monotonic_time, use_abbreviation = True)

                    if index == len(tasks) - 1:
                        text_buffer.append(f"└ [{task_id}]")
                        text_buffer.append(f"  ├ Start for {start_formatted}")
                        text_buffer.append(f"  ├ Running for {formatted_running_time_ms}ms")
                        text_buffer.append(f"  └ Running for {formatted_running_time}")
                    else:
                        text_buffer.append(f"├ [{task_id}]")
                        text_buffer.append(f"│ ├ Start for {start_formatted}")
                        text_buffer.append(f"│ ├ Running for {formatted_running_time_ms}ms")
                        text_buffer.append(f"│ └ Running for {formatted_running_time}")
            
            text = "\n".join(text_buffer)
            await send_msg.send_check_length_prompt(text, code_block = True)
        else:
            await send_msg.send_error("No running tasks.")
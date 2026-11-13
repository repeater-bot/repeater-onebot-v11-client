import asyncio

from typing import Any, Type
from nonebot.adapters.onebot.v11 import Message
from ...assist import PersonaInfo, SendMsg, Variables
from ...cmd_info import CmdTypes
from ...command_register import(
    CommandCaller,
    CommandPackage
)
from ._parse_input import parse_input
from ._split_by_indent import split_by_indent
from ._fill_var import fill_var

@CommandCaller.register
class Parallel(CommandPackage):
    cmd = "parallel"
    aliases = {
        "par",
        "PAR",
        "Parallel",
        "PARALLEL",
    }
    cmd_type = CmdTypes.CONTROL
    description = f"""
        Execute Commands Parallelly

        Usage:
        
        ```
        /{cmd}
        /cmd1_trigger cmd1_args...
        /cmd2_trigger
            cmd2_args1
            cmd2_args
            ...
        /cmd3_trigger cmd3_args...
        ...
        ```
    """

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        lines = split_by_indent(persona_info.message)
        try:
            command_call: list[tuple[Type[CommandPackage[Any]], Message]] = parse_input(lines)
        except ValueError as e:
            await send_msg.send_error(f"Invalid Input Format: {e}")
        except KeyError as e:
            await send_msg.send_error(f"Unknown Command: {e}")
        
        async with CommandCaller.variable_lock:
            user_variables = CommandCaller.variables.setdefault(persona_info.namespace, Variables())
        
        tasks: list[asyncio.Task[Any]] = []
        for index, (package, args) in enumerate(command_call):
            try:
                package_instance = CommandCaller.get_instance(package)
            except KeyError:
                await send_msg.send_error(f"[{index}] Handler instance not found")
                send_msg.break_handler()
            copied_persona_info = persona_info.copy(args = args)
            copied_send_msg = send_msg.copy(
                component = package_instance.component
            )
            tasks.append(
                asyncio.create_task(
                    CommandCaller.horizontal_call(
                        package_instance,
                        persona_info = fill_var(copied_persona_info, user_variables),
                        send_msg = copied_send_msg
                    )
                )
            )
        
        results = await asyncio.gather(*tasks)
from typing import Any, Type
from nonebot.adapters.onebot.v11 import Message
from ...assist import (
    PersonaInfo,
    SendMsg,
    SendingTarget,
    Variables
)
from ...cmd_info import CmdTypes
from ...command_register import(
    CommandCaller,
    CommandPackage,
    SubCmdBreaked
)
from ._parse_input import parse_input
from ._split_by_indent import split_by_indent
from ._fill_var import fill_var

@CommandCaller.register
class Cascade(CommandPackage):
    cmd = "cascade"
    aliases = {
        "cas",
        "CAS",
        "Cascade",
        "CASCADE",
    }
    cmd_type = CmdTypes.CONTROL
    description = f"""
        Takes the result of the previous command as input to the next command.
        When args exist, use them instead of what was returned by the previous command.
        Use {{message}} to include the output of the previous entry in args,
        if there is no way to pass the previous line, the result is printed directly.

        Usage:
        ```
        /{cmd}
        /cmd1_trigger cmd1_args...
        /cmd2_trigger
          cmd2_args1
          cmd2_args2
          ...
        /cmd3_trigger
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
        
        tasks: list[tuple[CommandPackage[Any], PersonaInfo]] = []
        for index, (package, args) in enumerate(command_call):
            try:
                package_instance = CommandCaller.get_instance(package)
                copyed_persona_info = persona_info.copy(args = args)
                tasks.append((package_instance, copyed_persona_info))
            except KeyError:
                await send_msg.send_error(f"[{index}] Handler instance not found")
                send_msg.break_handler()
        
        last_result: PersonaInfo = persona_info.copy(args = persona_info.make_message())
        last_code: int | None = None
        async with CommandCaller.variable_lock:
            user_variables = CommandCaller.variables.setdefault(persona_info.namespace, Variables())
        for index, (package_instance, info) in enumerate(tasks):
            copyed_send_msg = send_msg.copy(
                component = package_instance.component
            )

            # 如果当前命令无参数且有上一步结果，使用上一步结果
            if info:
                messages: list[str] = str(info.message).splitlines()
                new_messages: list[str] = []
                for message in messages:
                    if not message.startswith(" "):
                        new_messages.append(
                            message.replace(
                                "{message}",
                                str(last_result.message)
                            )
                        )
                    else:
                        new_messages.append(message)
                
                info = info.copy(
                    args = persona_info.make_message(
                        "\n".join(new_messages)
                    )
                )
            elif not info and last_result:
                info = last_result
            elif index != 0:
                await copyed_send_msg.send_any(last_result.message)
                continue
            
            copyed_send_msg.sending_target = SendingTarget.BUFFER
            
            result = await CommandCaller.horizontal_call(
                package_instance,
                fill_var(info, user_variables),
                copyed_send_msg
            )

            if isinstance(result, SubCmdBreaked):
                last_code = result.code
            else:
                last_code = None
            
            current_result = Message()
            while copyed_send_msg.buffer.qsize() > 0:
                buffer_result = await copyed_send_msg.buffer.get()
                new_message = buffer_result.message
                if isinstance(new_message, Message):
                    current_result.extend(new_message)
                else:
                    current_result.append(new_message)
            
            last_result = info.copy(args = current_result)
        
        if last_result:
            last_result_message = last_result.message
            await send_msg.send_any(
                last_result_message,
                reply = False,
                break_code = last_code or 0
            )
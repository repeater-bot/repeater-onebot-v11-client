import re
import asyncio

from ...assist import PersonaInfo, SendMsg, SendType
from ...cmd_info import CmdTypes
from ...command_register import(
    CommandCaller,
    CommandPackage
)

@CommandCaller.register
class TimeoutAndCancel(CommandPackage):
    cmd = "timeoutAndCancel"
    aliases = {
        "tac",
        "TAC",
        "timeout_and_cancel",
        "Timeout_And_Cancel",
        "TimeoutAndCancel",
        "TIMEOUT_AND_CANCEL"
    }
    cmd_type = CmdTypes.CONTROL
    description = f"""
        Executes a command with timeout, and cancels it if it takes too long.

        Usage:
        ```
        /{cmd} timeout: command [args]
        ```
    """

    pattern = re.compile(r"^(?P<timeout>[\d\.]+)\s*:\s*(?P<command>[/\w\.]+)\s*(?P<args>.*)$", re.IGNORECASE | re.DOTALL | re.UNICODE)

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        msg = str(persona_info.message)
        
        matched = self.pattern.match(msg)
        if matched:
            timeout_str = matched.group("timeout")
            command = matched.group("command")
            args_prefix = matched.group("args")

            assert isinstance(timeout_str, str), "timeout_str must be str"
            assert isinstance(command, str), "command must be str"
            assert isinstance(args_prefix, str), "args_prefix must be str"

            try:
                timeout = float(timeout_str)
            except ValueError:
                await send_msg.send_error("Invalid timeout format")

            args = persona_info.make_message(args_prefix)

            try:
                package = CommandCaller.match_trigger_or_component(command)
            except KeyError:
                await send_msg.send_error(f"Command {command} not found")
                return
            
            try:
                package_instance = CommandCaller.get_instance(package)
            except KeyError as e:
                await send_msg.send_error(f"Command {command} instance not found: {e}")
                return

            copied_persona_info = persona_info.copy(
                args = args
            )
            copied_send_msg = send_msg.copy(
                component = package_instance.component,
                send_target = SendType.NULL
            )
            running = await CommandCaller.horizontal_enter_wait_created(
                package_instance,
                copied_persona_info,
                copied_send_msg
            )

            try:
                result = await asyncio.wait_for(
                    asyncio.shield(
                        running.task
                    ),
                    timeout = timeout
                )
                return result
            except asyncio.TimeoutError:
                await send_msg.send_prompt(f"Command \"{package_instance.component}\" timeout", continue_handler = True)
                running.cancel()
                send_msg.break_handler()
        else:
            await send_msg.send_error("Invalid command format")
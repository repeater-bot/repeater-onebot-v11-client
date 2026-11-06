import re

from ...assist import PersonaInfo, SendMsg
from ...cmd_info import CmdTypes
from ...command_register import(
    CommandCaller,
    CommandPackage,
    SubCmdBreaked,
)
from ...logger import logger

@CommandCaller.register
class Loop(CommandPackage):
    cmd = "loop"
    aliases = {
        "l",
        "L",
        "Loop",
        "LOOP"
    }
    cmd_type = CmdTypes.CONTROL
    description = f"""
    Execute a command in a loop
    When Times is not populated, it runs in a loop until the loop body command succeeds, similar to the while loop.
    When Times is filled, it must be executed multiple Times, whether it ends properly or not, like a for loop.
    When Times is preceded by an asterisk, it loops until the loop body command succeeds or the specified maximum number of Times is reached.

        Usage:
        ```
        /{cmd} times command [args]
        /{cmd} *times command [args]
        /{cmd} command [args]
        ```
    """

    pattern = re.compile(r"^(?P<times>\*?\d*)\s*(?P<command>[/\w_\.]+)\s*(?P<args>.*)$", re.IGNORECASE | re.DOTALL | re.UNICODE)

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        matched = self.pattern.match(persona_info.message_cqcode)
        if matched:
            times_str = matched.group("times")
            command = matched.group("command")
            args_str = matched.group("args")

            assert isinstance(times_str, str), "times_str must be str"
            assert isinstance(command, str), "command must be str"
            assert isinstance(args_str, str), "args_str must be str"

            args = persona_info.make_message(args_str)

            try:
                if not times_str:
                    times = None
                    max_times = None
                elif times_str.startswith("*"):
                    times = None
                    max_times = int(times_str.removeprefix("*"))
                else:
                    times = int(times_str)
                    max_times = times
                
                    if times < 1:
                        await send_msg.send_error("times must be greater than 0")
                        return
            except ValueError:
                await send_msg.send_error("times must be int or [int]")
                return

            try:
                package = CommandCaller.match_trigger_or_component(command)
            except KeyError:
                await send_msg.send_error(f"Command {command} not found")
                return
            
            try:
                package_instance = CommandCaller.get_instance(package)
            except KeyError as e:
                await send_msg.send_error(f"Command instance {command} not found: {e}")
                return

            copied_persona_info = persona_info.copy(
                args = args
            )
            copied_send_msg = send_msg.copy(
                component = package_instance.component
            )
            if times is None:
                times_count: int = 0
                while True:
                    logger.info(
                        "Looping command times: {times_count}",
                        times_count = times_count + 1
                    )
                    result = await CommandCaller.horizontal_call(
                        package_instance,
                        copied_persona_info,
                        copied_send_msg
                    )

                    if isinstance(result, SubCmdBreaked):
                        if result.code == 0:
                            break

                    times_count += 1
                    if max_times is not None and times_count >= max_times:
                        break
            else:
                for i in range(times):
                    logger.info(
                        "Looping command times: {times_count}",
                        times_count = i + 1
                    )
                    await CommandCaller.horizontal_call(
                        package_instance,
                        copied_persona_info,
                        copied_send_msg
                    )
        else:
            await send_msg.send_error("Invalid command format")
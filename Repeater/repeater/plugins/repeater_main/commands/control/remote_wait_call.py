import re
import asyncio

from typing import Any, Type
from ...assist import PersonaInfo, SendMsg, Namespace
from ...cmd_info import CmdTypes
from ...command_register import(
    CommandCaller,
    CommandPackage
)
from ._remove_cmd_prefix import remove_cmd_prefix

@CommandCaller.register
class RemoteWaitCall(CommandPackage):
    cmd = "remoteWaitCall"
    aliases = {
        "rwc",
        "RWC",
        "remote_wait_call",
        "Remote_Wait_Call",
        "RemoteWaitCall",
        "REMOTE_WAIT_CALL"
    }
    cmd_type = CmdTypes.CONTROL
    description = f"""
        Wait for last remote input to be called.

        Usage:
        ```
        /{cmd} namespace times command [args]
        ```
    """
    super_permissions = True

    pattern = re.compile(r"^(?P<namespace>[a-zA-Z0-9_]+)\s*(?P<times>\d*)\s*(?P<command>[/\w_\.]+)\s*(?P<args>.*)$", re.IGNORECASE | re.DOTALL | re.UNICODE)

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg) -> None:
        msg = persona_info.message_cqcode
        matched = self.pattern.match(msg)
        if matched:
            namespace_str = matched.group("namespace")
            times_str = matched.group("times")
            command = matched.group("command")
            args_str = matched.group("args")

            assert isinstance(namespace_str, str), "mode must be str"
            assert isinstance(times_str, str), "times_str must be str"
            assert isinstance(command, str), "command must be str"
            assert isinstance(args_str, str), "args must be str"

            if not times_str:
                times = 1
            else:
                times = int(times_str)
            
            if times < 1:
                await send_msg.send_error("Times must be greater than 0")
                return
            try:
                namespace = Namespace.from_str(namespace_str)
            except ValueError:
                await send_msg.send_error("Invalid namespace")
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

            result: PersonaInfo = persona_info
            for i in range(times):
                result = await CommandCaller.wait_message(
                    namespace
                )

            if args_str.strip():
                args = persona_info.make_message(args_str.replace("{message}", result.message_cqcode))
            else:
                args = persona_info.make_message(result.message_cqcode)

            info = result.copy(args = args)
            
            copied_send_msg = send_msg.copy(
                component = package_instance.component
            )
            await CommandCaller.horizontal_call(
                package_instance,
                info,
                copied_send_msg
            )
        else:
            await send_msg.send_error("Invalid command format")
import re

from ...assist import PersonaInfo, SendMsg, SendType
from ...cmd_info import CmdTypes
from ...command_register import(
    CommandCaller,
    CommandPackage
)

@CommandCaller.register
class Scheduling(CommandPackage):
    cmd = "scheduling"
    aliases = {
        "scdl",
        "SCDL",
        "Scheduling",
        "SCEDULING"
    }
    cmd_type = CmdTypes.CONTROL
    description = f"""
        Create a scheduled task using a cron expression.

        6 Digital CRON Expression:
        ```
        * * * * * 0
        │ │ │ │ │ └ second (0 - 59)
        │ │ │ │ └── weekday (0 - 7, 0 and 7 = Sunday)
        │ │ │ └──── month (1 - 12)
        │ │ └────── day (1 - 31)
        │ └──────── hour (0 - 23)
        └────────── minute (0 - 59)
        ```

        5 Digital CRON Expression:
        ```
        0 * * * *
        │ │ │ │ └── weekday (0 - 7, 0 and 7 = Sunday)
        │ │ │ └──── month (1 - 12)
        │ │ └────── day (1 - 31)
        │ └──────── hour (0 - 23)
        └────────── minute (0 - 59)
        ```
        If the month does not have the required date (such as the 31st, 30th, 29th, etc.) , the system skips the month and matches the next month that has the required date.
        The scheduler runs entirely in memory and is canceled if the server is down or if the command is canceled.

        Usage:
        ```
        /{cmd} {{cron_expression}} command [args]
        ```
        PS: The curly braces need to be retained here to ensure that the cron expression resolves properly.
    """

    pattern = re.compile(r"^\{(?P<cron_expression>.*)\}\s*(?P<components_or_trigger>[/\w_\.]+)\s*(?P<args>.*)$", re.IGNORECASE | re.DOTALL | re.UNICODE)

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        msg = str(persona_info.message)
        
        matched = self.pattern.match(msg)
        if matched:
            cron = matched.group("cron_expression")
            components_or_trigger = matched.group("components_or_trigger")
            args_prefix = matched.group("args")

            assert isinstance(cron, str), "cron must be str"
            assert isinstance(components_or_trigger, str), "components must be str"
            assert isinstance(args_prefix, str), "args_prefix must be str"

            args = persona_info.make_message(args_prefix)

            try:
                package = CommandCaller.match_trigger_or_component(components_or_trigger)
            except KeyError:
                await send_msg.send_error(f"Command {components_or_trigger} not found")
                return
            
            try:
                package_instance = CommandCaller.get_instance(package)
            except KeyError as e:
                await send_msg.send_error(f"Command instance {package.component} not found: {e}")
                return

            copied_persona_info = persona_info.copy(
                args = args
            )
            copied_send_msg = send_msg.copy(
                component = package_instance.component
            )
            try:
                await CommandCaller.timed_scheduling(
                    package = package_instance,
                    cron = cron,
                    persona_info = copied_persona_info,
                    send_msg = copied_send_msg
                )
            except ValueError as e:
                await send_msg.send_error(f"Cron format error: {e}")
        else:
            await send_msg.send_error("Invalid command format")
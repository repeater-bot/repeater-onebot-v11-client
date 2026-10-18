from ...assist import PersonaInfo, SendMsg, SendingTarget
from ...cmd_info import CmdTypes
from ...command_register import(
    CommandCaller,
    CommandPackage
)
from ._peel_command import peel_command

@CommandCaller.register
class RenderToText(CommandPackage):
    cmd = "renderToText"
    aliases = {
        "rtt",
        "RTT",
        "render_to_text",
        "Render_To_Text",
        "RenderToText",
        "RENDER_TO_TEXT"
    }
    cmd_type = CmdTypes.CONTROL
    description = f"""
        Gets the text of Render.

        Usage:
        ```
        /{cmd} command [args]
        ```
    """

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        peeled = peel_command(persona_info.message)
        if peeled is not None:
            components_or_trigger, args = peeled

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

            texts: list[str] = []

            async def render_hook(
                text: str,
                style: str | None = None,
                image_expiry_time: int | None = None,
                html_template: str | None = None,
                title: str | None = None,
                document_bottom_comment: str | None = None,
                width: int | None = None,
                height: int | None = None,
                direct_output: bool | None = None,
                no_pre_labels: bool | None = None,
                no_escape: bool | None = None,
                quality: int | None = None
            ) -> None:
                nonlocal texts
                texts.append(text)

            copyed_persona_info = persona_info.copy(
                args = args
            )
            copyed_send_msg = send_msg.copy(
                component = package_instance.component,
                send_target = SendingTarget.API,
                render_hook = render_hook
            )
            result = await CommandCaller.horizontal_call(
                package_instance,
                copyed_persona_info,
                copyed_send_msg
            )
            for text in texts:
                await send_msg.send_text(text, continue_handler = True)
            return result
        else:
            await send_msg.send_error("Invalid command format")
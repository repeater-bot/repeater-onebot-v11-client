from ....assist import PersonaInfo, SendMsg
from ....cmd_info import CmdTypes
from ....command_register import(
    CommandCaller,
    CommandPackage
)
from ....clients import PromptClient


@CommandCaller.register
class SendRenderPromptFile(CommandPackage):
    cmd = "sendRenderPromptFile"
    aliases = {
        "srpf",
        "SRPF",
        "send_render_prompt_file",
        "Send_Render_Prompt_File",
        "SendRenderPromptFile",
        "SEND_RENDER_PROMPT_FILE",
    }
    cmd_type = CmdTypes.PROMPT
    description = f"""
    Export the render prompt file.

    Usage:
    ```
    /{cmd}
    ```
    """

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        user_configs = await persona_info.get_user_configs()
        prompt_client = PromptClient(persona_info, user_configs)
        file_url = prompt_client.render_prompt_file_url()
        await send_msg.send_file(file_url, f"{persona_info.namespace_str}_Rendered_Prompt.md")
from ....assist import PersonaInfo, SendMsg
from ....cmd_info import CmdTypes
from ....command_register import(
    CommandCaller,
    CommandPackage
)
from ....clients import PromptClient

@CommandCaller.register
class SetPrompt(CommandPackage):
    cmd = "setPrompt"
    aliases = {
        "sp",
        "SP",
        "set_prompt",
        "Set_Prompt",
        "SetPrompt",
        "SET_PROMPT",
    }
    cmd_type = CmdTypes.PROMPT
    description = f"""
    Set user custom prompt.

    Usage:
    ```
    /{cmd}
    ```
    """


    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        msg = persona_info.message_stripped_str

        user_configs = await persona_info.get_user_configs()
        prompt_client = PromptClient(persona_info, user_configs)
        response = await prompt_client.set_prompt(msg)
        await send_msg.send_response_check_code(response, f"Set Prompt {'successfully' if response else 'failed'}")
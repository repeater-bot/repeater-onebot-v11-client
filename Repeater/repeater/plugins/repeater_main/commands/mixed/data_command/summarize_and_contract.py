from ....clients import (
    ChatClient,
    ContextClient
)
from ....command_register import CommandCaller
from ....assist import PersonaInfo, SendMsg
from ..._bases import BaseChat
from ....cmd_info import CmdTypes
from ._default_sac_prompt import DEFAULT_SAC_PROMPT, DEFAULT_SAC_FINISHED_PROMPT

@CommandCaller.register
class SummarizeAndContract(BaseChat):
    cmd = "summarizeAndContract"
    aliases = {
        "sac",
        "SAC",
        "summarize_and_contract",
        "Summarize_And_Contract",
        "SummarizeAndContract",
        "SUMARAIZE_AND_CONTRACT"
    }
    cmd_type = CmdTypes.MIXED
    description = f"""
        Summarizes the user's contextual content
        And save only summary information

        Usage:
        ```
        /{cmd} new_branch_id
        ```
    """
    async def get_client(self, persona_info: PersonaInfo) -> tuple[ChatClient, ContextClient]:
        user_configs = await persona_info.get_user_configs()
        chat_client = ChatClient(persona_info, user_configs)
        config_client = ContextClient(persona_info, user_configs)
        return chat_client, config_client

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        chat_client, context_client = await self.get_client(persona_info)
        response = await chat_client.send_message(
            message = DEFAULT_SAC_PROMPT,
            raw_message = True
        )
        chat_send_msg = self.make_send_msg(send_msg, response)
        content = chat_send_msg.content
        if content is None:
            await send_msg.send_error("No content found")
            return

        change_context_response = await context_client.change_branch(
            new_branch_id = persona_info.message_stripped_str
        )
        if change_context_response is None:
            await send_msg.send_error("Failed to delete context")
            return

        second_chat_response = await chat_client.send_message(
            message = DEFAULT_SAC_FINISHED_PROMPT.format(summary = content)
        )

        await send_msg.send_prompt("Summarized and contracted")
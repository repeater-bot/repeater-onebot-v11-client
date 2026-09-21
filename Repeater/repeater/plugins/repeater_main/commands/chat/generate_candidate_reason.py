import re
from ...logger import logger

from ...clients import ChatClient, ContentRole, ChatResponse
from ...assist import PersonaInfo, SendMsg, Response
from ...command_register import CommandCaller
from .._bases import BaseChat, SendMessage

@CommandCaller.register
class GenerateCandidateReason(BaseChat):
    cmd = "generateCandidateReason"
    aliases = {
        "gcr",
        "GCR",
        "generate_candidate_reason",
        "Generate_Candidate_Reason",
        "GenerateCandidateReason",
        "GENERATE_CANDIDATE_REASON"
    }
    description = f"""
        Initiate a text generation request in the opposite role and enable inference mode,
        let AI simulate user-generated content.
        Warning: the presence of a tool call may cause an application error.
        
        Usage:
        ```
        /{cmd}
        ```
    """
    no_input = True
    
    async def send_message(
        self,
        client: ChatClient,
        send_messages: SendMessage,
        persona_info: PersonaInfo,
        send_msg: SendMsg
    ) -> Response[ChatResponse]:

        response = await client.send_message(
            message = None,
            raw_message = False,
            save_context = False,
            temporary_prompt = (
                "{%- if user_profile -%}\n"
                "{{user_profile}}\n"
                "{%- endif %}"
            ),
            history_msg_role_map = {
                ContentRole.USER: ContentRole.ASSISTANT,
                ContentRole.ASSISTANT: ContentRole.USER,
                ContentRole.SYSTEM: None,
                ContentRole.TOOL: None
            }
        )
        return response

    @staticmethod
    def filters(message: str) -> str:
        return ChatClient.metadata_pattern.sub("", message)
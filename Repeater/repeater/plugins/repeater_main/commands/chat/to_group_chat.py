import re
from .._bases import BaseChat
from ...assist import PersonaInfo
from ...clients import ChatClient
from ...command_register import CommandCaller

@CommandCaller.register
class ToGroupChat(BaseChat):
    cmd = "toGroupChat"
    aliases = {
        "tgc",
        "TGC",
        "to_group_chat",
        "To_Group_Chat",
        "ToGroupChat",
        "TO_GROUP_CHAT"
    }
    description = f"""
        Submits a build request
        using the user identity under the specified group number
        
        Usage:
        ```
        /{cmd} group_id text
        ```
    """
    pattern = re.compile(r"^(?P<group_id>\d+)\s*(?P<text>.*)$", re.DOTALL)

    async def parse_input_text(self, persona_info: PersonaInfo, text: str) -> str:
        matched = self.pattern.match(text)
        if matched:
            message_text = matched.group("text")
            assert isinstance(message_text, str), "The text must be a string"
        else:
            raise ValueError("Invalid input format")
        
        return message_text
    
    async def get_client(self, persona_info: PersonaInfo) -> ChatClient:
        matched = self.pattern.match(persona_info.message_stripped_str)
        if matched:
            group_id_str = matched.group("group_id")
            assert isinstance(group_id_str, str), "The group_id must be a string"
            group_id = group_id_str
        else:
            raise ValueError("Invalid input format")
        
        user_configs = await persona_info.get_user_configs()
        client = ChatClient(
            persona_info,
            user_configs,
            namespace = persona_info.group_namespace(group_id),
        )
        return client
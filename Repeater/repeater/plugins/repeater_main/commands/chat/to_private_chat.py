from .._bases import BaseChat
from ...assist import PersonaInfo
from ...clients import ChatClient
from ...command_register import CommandCaller

@CommandCaller.register
class ToPrivateChat(BaseChat):
    cmd = "toPrivateChat"
    aliases = {
        "tpc",
        "TPC",
        "to_private_chat",
        "To_Private_Chat",
        "ToPrivateChat",
        "TO_PRIVATE_CHAT"
    }
    description = f"""
        Send a build request as a private chat.
        
        Usage:
        ```
        /{cmd} text
        ```
    """
    
    async def get_client(self, persona_info: PersonaInfo) -> ChatClient:
        user_configs = await persona_info.get_user_configs()
        client = ChatClient(
            persona_info,
            user_configs = user_configs,
            namespace = persona_info.private_namespace,
        )
        return client
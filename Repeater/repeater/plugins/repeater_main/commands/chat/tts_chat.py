from .._bases import BaseChat
from ...clients import ChatSendMsg
from ...command_register import CommandCaller

@CommandCaller.register
class TTSChat(BaseChat):
    cmd = "tts_chat"
    aliases = {
        "ttsc",
        "TTSC",
        "tts_Chat",
        "TTS_Chat",
        "TTSChat",
        "TTS_CHAT",
    }
    description = f"""
        Initiates a text generation request,
        Return content to force tts output.
        
        Usage:
        ```
        /{cmd} text
        ```
    """

    async def send_chat_send_msg(
        self,
        chat_send_msg: ChatSendMsg,
        reply: bool = True,
        break_code: int = 0,
        continue_handler: bool = False
    ):
        await chat_send_msg.send_tts_mode(
            reply=reply,
            break_code=break_code,
            continue_handler=continue_handler
        )
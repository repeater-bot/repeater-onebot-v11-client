from .._bases import BaseChat
from ...clients import ChatSendMsg
from ...command_register import CommandCaller, CommandPackage

@CommandCaller.register
class TextChat(BaseChat):
    cmd = "textChat"
    aliases = {
        "txc",
        "TXC",
        "text_chat",
        "Text_Chat",
        "TextChat",
        "TEXTCHAT"
    }
    description = f"""
        Initiates a text generation request
        Return all to force text output.
        
        Usage:
        ```
        /{cmd} text
        ```
    """

    async def send_chat_send_msg(
        self,
        chat_send_msg: ChatSendMsg,
    ):
        await chat_send_msg.send_text_mode(
            reasoning_content_to_image = False,
            tool_response_to_image = False
        )
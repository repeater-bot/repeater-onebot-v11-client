from .._bases import BaseChat
from ...clients import ChatSendMsg
from ...command_register import CommandCaller
from ...client_configs import ChatOutputMode

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
        reply: bool = True,
        break_code: int = 0,
        continue_handler: bool = False
    ):
        await chat_send_msg.send(
            output_reasoning_content_mode = ChatOutputMode.TEXT,
            output_tool_call_mode = ChatOutputMode.TEXT,
            output_content_mode = ChatOutputMode.TEXT,
            reply = reply,
            break_code = break_code,
            continue_handler = continue_handler
        )
import re

from ....assist import PersonaInfo, SendMsg, Response
from ....cmd_info import CmdTypes
from ....clients import ChatClient, ChatResponse, ChatSendMsg
from ..base_chat.base_chat_pkg import BaseChat, SendMessage
from typing import ClassVar
from ....logger import logger

class BaseFIM(BaseChat):
    echo: ClassVar[bool | None] = None
    cmd_type = CmdTypes.FIM

    fim_regex = re.compile(r"^(?P<prompt>.*?)\[fill_this\](?P<suffix>.*)$", re.IGNORECASE | re.DOTALL)
    fim_regex_greedy = re.compile(r"^(?P<prompt>.*)_{3,}(?P<suffix>.*)$", re.IGNORECASE | re.DOTALL)

    async def parse_message(
        self,
        persona_info: PersonaInfo,
        send_msg: SendMsg
    ) -> SendMessage:
        if self.echo:
            text = persona_info.message_stripped_str
        else:
            msg = persona_info.message_stripped_str
            match_fim = self.fim_regex.match(msg)
            if match_fim:
                text = match_fim.group("prompt")
                suffix = match_fim.group("suffix")
                
                assert isinstance(text, str), "text must be a string"
                assert isinstance(suffix, str), "suffix must be a string"
                
                return SendMessage(text=text, suffix=suffix)
            else:
                match_fim_greedy = self.fim_regex_greedy.match(msg)
                if match_fim_greedy:
                    text = match_fim_greedy.group("prompt")
                    suffix = match_fim_greedy.group("suffix")

                    assert isinstance(text, str), "text must be a string"
                    assert isinstance(suffix, str), "suffix must be a string"
                    
                    return SendMessage(text=text, suffix=suffix)
                else:
                    await send_msg.send_error("Invalid FIM format")

        return SendMessage(text=text)

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        logger.info(
            "Received a message {message} from {namespace}",
            message = persona_info.message_stripped_str,
            namespace = persona_info.namespace_str,
            module = send_msg.component
        )
        
        client = await self.get_client(persona_info)

        message = await self.parse_message(persona_info, send_msg)

        response = await self.send_message(
            client = client,
            send_messages = message,
            suffix = message.suffix,
            persona_info = persona_info,
            send_msg = send_msg
        )

        def filters(text: str) -> str:
            nonlocal self
            if self.echo:
                return text
            else:
                buffer: list[str] = []
                if message.text:
                    buffer.append(message.text)
                if text:
                    buffer.append(text)
                if message.suffix:
                    buffer.append(message.suffix)
                return "".join(buffer)
        
        chat_send_msg = self.make_send_msg(send_msg, response)
        await self.send_chat_send_msg(chat_send_msg)
    
    async def send_message(
        self,
        client: ChatClient,
        send_messages: SendMessage,
        suffix: str | None,
        persona_info: PersonaInfo,
        send_msg: SendMsg
    ) -> Response[ChatResponse]:
        response: Response[ChatResponse] = await client.send_message(
            message = send_messages.text,
            image_url = send_messages.images,
            audio_url = send_messages.audios,
            video_url = send_messages.videos,
            file_url = send_messages.files,
            suffix = suffix,
            fim_mode = True,
            raw_message = False
        )
        return response
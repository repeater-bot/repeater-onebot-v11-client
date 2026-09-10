import asyncio

from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.internal.matcher.matcher import Matcher
from typing import NoReturn, Type, Callable

from ....assist import (
    PersonaInfo,
    Response,
    SendMsg,
    ChatTTSAPI,
    ErrorResponse,
    text_content_cutter,
)
from ..response_body import ChatResponse
from ...content_role import ContentRole
from ....logger import logger as base_logger
from ....client_configs import storage_configs

logger = base_logger.bind(module = "Chat.SendMsg")

class ChatSendMsg(SendMsg):
    def __init__(
            self,
            component: str,
            persona_info: PersonaInfo,
            response: Response[ChatResponse],
            matcher: Type[Matcher] | None = None,
            reasoning_content_handler: Callable[[str], str] = lambda t: t,
            content_handler: Callable[[str], str] = lambda t: t,
            strip: bool = True,
        ):
        super().__init__(
            component = component,
            persona_info = persona_info,
            matcher = matcher,
        )
        self._response: Response[ChatResponse] = response
        self._chat_tts_api = ChatTTSAPI()
        self._reasoning_content_handler = reasoning_content_handler
        self._content_handler = content_handler
        self._strip = strip
        if self._response.initialized:
            self._data: ChatResponse | None = self._response.get_data()
            self._error: Response[ErrorResponse] | None = self._response.to_error()
        else:
            self._data = None
            self._error = None
    
    @property
    def reasoning_content(self) -> str | None:
        if self._data is None:
            return None
        buffer: list[str] = []
        for content in self._data.context.context_list:
            if content.role == ContentRole.ASSISTANT:
                if content.reasoning_content and content.reasoning_content.strip():
                    buffer.append(content.reasoning_content)
        merged_content = "\n\n---\n\n".join(buffer)
        if self._strip:
            merged_content = merged_content.strip()
        return self._reasoning_content_handler(merged_content)

    @property
    def tools_content(self) -> str | None:
        return self.get_tools_content(
            response_max_length = storage_configs.max_tool_response_length
        )

    def get_tools_content(self, response_max_length: int | None = 100):
        if self._data is None:
            return None
        buffer: list[str] = []
        for content in self._data.context.context_list:
            if content.role == ContentRole.ASSISTANT:
                if content.tool_calls:
                    for tool_call in content.tool_calls:
                        sub_buffer: list[str] = []
                        sub_buffer.append(f"[Call Tool] {tool_call.function.name}({tool_call.id})")
                        sub_buffer.append("```")
                        sub_buffer.append(tool_call.function.arguments)
                        sub_buffer.append("```")
                        buffer.append("\n".join(sub_buffer))
            if content.role == ContentRole.TOOL:
                if content.tool_call_id:
                    sub_buffer: list[str] = []
                    sub_buffer.append(f"[Tool Response] {content.tool_call_id}")
                    sub_buffer.append("```")
                    if response_max_length is not None:
                        sub_buffer.append(text_content_cutter(content.content, response_max_length))
                    else:
                        sub_buffer.append(content.content)
                    sub_buffer.append("```")
                    buffer.append("\n".join(sub_buffer))

        return "\n\n".join(buffer)

    @property
    def content(self) -> str | None:
        if self._data is None:
            return None
        buffer: list[str] = []
        for content in self._data.context.context_list:
            if content.role == ContentRole.ASSISTANT:
                if content.content and content.content.strip():
                    buffer.append(content.content)
        merged_content = "\n\n---\n\n".join(buffer)
        if self._strip:
            merged_content = merged_content.strip()
        return self._content_handler(merged_content)
    
    async def _check_response(self) -> None | NoReturn:
        if self.is_debug_mode:
            await self.send_debug_mode()
        
        if self._response.code != 200 and self._error is not None:
            await self.send_error_response(self._error)
        
        if self._response.exception_info and self._response.exception_info.exc_value is not None:
            await self.send_error(self._response.exception_info.exc_value)
    
    def _get_response_usage(self) -> str:
        if self._data is None:
            return ""
        return self._data.request_statistics
    
    async def send(self) -> NoReturn:
        await self._check_response()

        content = self.content
        if content is None:
            self.handler_finished()

        score = self.text_length_score(content)
        threshold = self.text_length_score_threshold
        logger.info(f"Response content score: {score}")
        if score >= threshold:
            logger.warning(f"Response content score to high: {score}, Expected to be below {threshold} ")
            logger.warning("The text will be rendered as an image output.")
            await self.send_image_mode()
        else:
            await self.send_text_mode()
    
    async def send_tts_mode(self, text: str | None = None) -> NoReturn:
        await self._check_response()

        if self.reasoning_content:
            await self.send_render(
                self.reasoning_content,
                reply = True,
                continue_handler = True
            )
        if self.content:
            await self.send_tts(
                text or self.content,
                reply = False,
                continue_handler = False
            )
        
        # This line is not necessary
        self.handler_finished()

    @staticmethod
    async def _content_to_text(msg: str, prefix: str = "", suffix: str = "\n\n---\n\n") -> MessageSegment:
        if msg:
            return MessageSegment.text(
                f"{prefix}{msg}{suffix}"
            )
        else:
            return MessageSegment.text("")
    
    async def send_text_mode(
            self,
            text: str | None = None,
            reasoning_content_to_image: bool = True,
            tool_response_to_image: bool = True
        ) -> NoReturn:
        await self._check_response()
        
        tasks: list[asyncio.Task[MessageSegment]] = []
        reasoning_content = self.reasoning_content
        tools_content = self.tools_content
        content = self.content

        if reasoning_content:
            if reasoning_content_to_image:
                reasoning_render_task = asyncio.create_task(
                    self.render_text_to_msg_segment(
                        reasoning_content,
                        document_bottom_comment = self._get_response_usage()
                    )
                )
                tasks.append(reasoning_render_task)
            else:
                tasks.append(
                    asyncio.create_task(
                        self._content_to_text(
                            reasoning_content
                        )
                    )
                )
        if tools_content:
            if tool_response_to_image:
                tool_response_render_task = asyncio.create_task(
                    self.render_text_to_msg_segment(
                        tools_content,
                        document_bottom_comment = self._get_response_usage()
                    )
                )
                tasks.append(tool_response_render_task)
            else:
                tasks.append(
                    asyncio.create_task(
                        self._content_to_text(
                            tools_content
                        )
                    )
                )
        if content:
            tasks.append(
                asyncio.create_task(
                    self._content_to_text(
                        text or content,
                        suffix = ""
                    )
                )
            )
        else:
            tasks.append(
                asyncio.create_task(
                    self.empty_message()
                )
            )

        results = await asyncio.gather(*tasks)
        message = Message(results)

        message.reduce()
        await self._send(message)

        # This line is not necessary
        self.handler_finished()
    
    async def send_image_mode(
            self,
            text: str | None = None
        ) -> NoReturn:
        await self._check_response()
        tasks: list[asyncio.Task[MessageSegment]] = []

        if self.reasoning_content:
            reason_render_task = asyncio.create_task(
                self.render_text_to_msg_segment(
                    self.reasoning_content,
                    document_bottom_comment = self._get_response_usage()
                )
            )
            tasks.append(reason_render_task)
        if self.tools_content:
            tools_render_task = asyncio.create_task(
                self.render_text_to_msg_segment(
                    self.tools_content,
                    document_bottom_comment = self._get_response_usage()
                )
            )
            tasks.append(tools_render_task)
        if self.content:
            content_render_task = asyncio.create_task(
                self.render_text_to_msg_segment(
                    text or self.content,
                    document_bottom_comment = self._get_response_usage()
                )
            )
            tasks.append(content_render_task)
        else:
            tasks.append(
                asyncio.create_task(
                    self.empty_message()
                )
            )
        
        if tasks:
            results = await asyncio.gather(*tasks)
            message = Message(results)
            await self._send(message)
        else:
            await self.send_error("Nothing can be sent.")
        
        # This line is not necessary
        self.handler_finished()
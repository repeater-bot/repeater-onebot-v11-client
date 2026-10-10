import asyncio

from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.internal.matcher.matcher import Matcher
from typing import NoReturn, Type, Callable, overload, Literal

from ....assist import (
    PersonaInfo,
    Response,
    SendMsg,
    SendingTarget,
    SEND_HOOK,
    RENDER_HOOK,
    ChatTTSAPI,
    ErrorResponse,
    text_content_cutter,
)
from ..response_body import ChatResponse
from ...content_role import ContentRole
from ....logger import logger as base_logger
from ....client_configs import storage_configs, ChatOutputMode
from typing_extensions import deprecated

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

            reply: MessageSegment | None = None,
            prefix: Message | None = None,
            suffix: Message | None = None,
            target_group: str | None = None,
            target_user: str | None = None,
            send_target: SendingTarget = SendingTarget.AUTO,
            send_hook: SEND_HOOK | None = None,
            render_hook: RENDER_HOOK | None = None,
        ):
        super().__init__(
            component = component,
            persona_info = persona_info,
            matcher = matcher,

            reply = reply,
            prefix = prefix,
            suffix = suffix,
            target_group = target_group,
            target_user = target_user,
            send_target = send_target,
            send_hook = send_hook,
            render_hook = render_hook,
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
    
    async def check_response(
        self,
        reply: bool = True,
        break_code: int = 0,
        continue_handler: bool = False
    ) -> None | NoReturn:
        if self.is_debug_mode:
            await self.send_debug_mode(
                reply = reply,
                break_code = break_code,
                continue_handler = continue_handler
            )
        
        elif self._response.code != 200 and self._error is not None:
            await self.send_error_response(
                self._error,
                reply = reply,
                break_code = break_code,
                continue_handler = continue_handler
            )
        
        elif self._response.exception_info and self._response.exception_info.exc_value is not None:
            await self.send_error(
                self._response.exception_info.exc_value,
                reply = reply,
                break_code = break_code,
                continue_handler = continue_handler
            )
    
    def _get_response_usage(self) -> str:
        if self._data is None:
            return ""
        return self._data.request_statistics

    @overload
    async def send(
            self,
            text: str | None = None,
            output_reasoning_content_mode: ChatOutputMode | None = None,
            output_tool_call_mode: ChatOutputMode | None = None,
            output_content_mode: ChatOutputMode | None = None,
        
            title: str | None = None,
            document_bottom_comment: str | None = None,
            style: str | None = None,
            html_template: str | None = None,

            reply: bool = True,
            break_code: int = 0,
            continue_handler: Literal[False] = False
        ) -> NoReturn: ...

    @overload
    async def send(
            self,
            text: str | None = None,
            output_reasoning_content_mode: ChatOutputMode | None = None,
            output_tool_call_mode: ChatOutputMode | None = None,
            output_content_mode: ChatOutputMode | None = None,
        
            title: str | None = None,
            document_bottom_comment: str | None = None,
            style: str | None = None,
            html_template: str | None = None,

            reply: bool = True,
            break_code: int = 0,
            continue_handler: Literal[True] = True
        ) -> None: ...
    
    async def send(
            self,
            text: str | None = None,
            output_reasoning_content_mode: ChatOutputMode | None = None,
            output_tool_call_mode: ChatOutputMode | None = None,
            output_content_mode: ChatOutputMode | None = None,
        
            title: str | None = None,
            document_bottom_comment: str | None = None,
            style: str | None = None,
            html_template: str | None = None,

            reply: bool = True,
            break_code: int = 0,
            continue_handler: bool = False
        ) -> None:
        """
        Parse Chat Response and send it.

        :param text: The text to send.
        :param output_reasoning_content_mode: The mode to output reasoning content.
        :param output_tool_call_mode: The mode to output tool call content.
        :param output_content_mode: The mode to output content.
        :param title: The title of the document.
        :param document_bottom_comment: The bottom comment of the document.
        :param style: The style of the document.
        :param html_template: The html template of the document.
        :param reply: Whether to reply to the message.
        :param break_code: The break code of the message.
        :param continue_handler: Whether to continue the handler.
        """

        await self.check_response(
            reply = reply,
            break_code = break_code,
            continue_handler = continue_handler
        )
        user_configs = await self.persona_info.get_user_configs()
        chat_output = user_configs.chat_output

        content = self.content
        if content is None:
            if continue_handler:
                return
            else:
                self.break_handler()
            
        output_reasoning_content_final_mode = (
            output_reasoning_content_mode or
            chat_output.reasoning_content or
            storage_configs.chat_output.reasoning_content
        )
        
        output_tool_call_final_mode = (
            output_tool_call_mode or
            chat_output.tool_content or
            storage_configs.chat_output.tool_content
        )

        output_content_final_mode = (
            output_content_mode or
            chat_output.content or
            storage_configs.chat_output.content
        )

        logger.info(
            "Chat Output Mode: {reasoning}/{tool}/{content}",
            reasoning = output_reasoning_content_mode,
            tool = output_tool_call_mode,
            content = output_content_mode
        )

        message = await self.parse_response(
            text = text or content,

            output_reasoning_content_mode = output_reasoning_content_final_mode,
            output_tool_call_mode = output_tool_call_final_mode,
            output_content_mode = output_content_final_mode,

            title = title,
            document_bottom_comment = document_bottom_comment,
            style = style,
            html_template = html_template
        )

        await self._send(
            message,
            reply = reply,
            break_code = break_code,
            continue_handler = continue_handler
        )

    @overload
    @deprecated("Compatible reserved, ready to be deprecated interface.")
    async def send_tts_mode(
            self,
            text: str | None = None,
            reply: bool = True,
            break_code: int = 0,
            continue_handler: Literal[False] = False
        ) -> NoReturn: ...

    @overload
    @deprecated("Compatible reserved, ready to be deprecated interface.")
    async def send_tts_mode(
            self,
            text: str | None = None,
            reply: bool = True,
            break_code: int = 0,
            continue_handler: Literal[True] = True
        ) -> None: ...

    @deprecated("Compatible reserved, ready to be deprecated interface.")
    async def send_tts_mode(
            self,
            text: str | None = None,
            reply: bool = True,
            break_code: int = 0,
            continue_handler: bool = False
        ) -> None:
        await self.check_response(
            reply = reply,
            break_code = break_code,
            continue_handler = continue_handler
        )

        if self.reasoning_content:
            await self.send_render(
                self.reasoning_content,
                reply=reply,
                break_code=break_code,
                continue_handler=continue_handler
            )
        if self.content:
            await self.send_tts(
                text or self.content,
                reply=reply,
                break_code=break_code,
                continue_handler=continue_handler
            )

    @staticmethod
    async def _content_to_text(
        msg: str,
    ) -> MessageSegment:
        return MessageSegment.text(text=msg)

    async def _spread_out_mode(
        self,
        output_mode: ChatOutputMode,
        content: str
    ) -> ChatOutputMode:
        if output_mode == ChatOutputMode.AUTO:
            tls = self.text_length_score(content)
            if tls > self.text_length_score_threshold:
                return ChatOutputMode.IMAGE
            else:
                return ChatOutputMode.TEXT
        else:
            return output_mode

    async def _parse_msg(
        self,
        output_mode: ChatOutputMode,
        content: str,
        
        title: str | None = None,
        document_bottom_comment: str | None = None,
        style: str | None = None,
        html_template: str | None = None,
    ) -> list[asyncio.Task[MessageSegment]]:
        tasks: list[asyncio.Task[MessageSegment]] = []
        match output_mode:
            case ChatOutputMode.IMAGE:
                reasoning_render_task = asyncio.create_task(
                    coro = self.render_text_to_msg_segment(
                        message = content,
                        title = title,
                        document_bottom_comment = document_bottom_comment or self._get_response_usage(),
                        style = style,
                        html_template = html_template
                    )
                )
                tasks.append(reasoning_render_task)
            case ChatOutputMode.TEXT:
                reasoning_text_task = asyncio.create_task(
                    coro = self._content_to_text(
                        msg = content
                    )
                )
                tasks.append(reasoning_text_task)
            case ChatOutputMode.AUTO:
                if self.text_length_score(content) > self.text_length_score_threshold:
                    reasoning_render_task = asyncio.create_task(
                        coro = self.render_text_to_msg_segment(
                            message = content,
                            title = title,
                            document_bottom_comment = document_bottom_comment or self._get_response_usage(),
                            style = style,
                            html_template = html_template
                        )
                    )
                    tasks.append(reasoning_render_task)
                else:
                    reasoning_text_task = asyncio.create_task(
                        coro = self._content_to_text(
                            msg = content
                        )
                    )
                    tasks.append(reasoning_text_task)
            case ChatOutputMode.NULL:
                pass
        return tasks
    
    async def parse_response(
            self,
            text: str | None = None,
            output_reasoning_content_mode: ChatOutputMode = ChatOutputMode.IMAGE,
            output_tool_call_mode: ChatOutputMode = ChatOutputMode.IMAGE,
            output_content_mode: ChatOutputMode = ChatOutputMode.AUTO,
        
            title: str | None = None,
            document_bottom_comment: str | None = None,
            style: str | None = None,
            html_template: str | None = None
        ) -> Message:
        tasks: list[asyncio.Task[MessageSegment]] = []
        reasoning_content = self.reasoning_content
        tools_content = self.tools_content
        content = self.content

        if reasoning_content:
            tasks.extend(
                await self._parse_msg(
                    output_mode = output_reasoning_content_mode,
                    content = reasoning_content,
                    title = title,
                    document_bottom_comment = document_bottom_comment,
                    style = style,
                    html_template = html_template
                )
            )
        if tools_content:
            tasks.extend(
                await self._parse_msg(
                    output_mode = output_tool_call_mode,
                    content = tools_content,
                    title = title,
                    document_bottom_comment = document_bottom_comment,
                    style = style,
                    html_template = html_template
                )
            )
        if content:
            tasks.extend(
                await self._parse_msg(
                    output_mode = output_content_mode,
                    content = text or content,
                    title = title,
                    document_bottom_comment = document_bottom_comment,
                    style = style,
                    html_template = html_template
                )
            )
        else:
            tasks.extend(
                await self._parse_msg(
                    output_mode = output_content_mode,
                    content = "[No Content]",
                    title = title,
                    document_bottom_comment = document_bottom_comment,
                    style = style,
                    html_template = html_template
                )
            )

        results = await asyncio.gather(*tasks)
        message = Message()
        for index, message_segment in enumerate(results):
            message.append(message_segment)
            if message_segment.type == "text" and index < len(results) - 1 and results[index + 1].type == "text":
                message.append(MessageSegment.text("\n\n---\n\n"))

        message.reduce()
        return message
import time
import asyncio

from io import BytesIO
from croniter import croniter
from datetime import datetime
from pathlib import Path
from nonebot.adapters.onebot.v11 import MessageSegment, Message
from nonebot.internal.matcher.matcher import Matcher
from nonebot.exception import FinishedException, ActionFailed

from ..assist_func import (
    text_length_score,
    send_group_file,
    send_private_file,
)
from ..text_render.text_render import RendedImage
from ...client_configs import REPEATER_DEBUG_MODE, storage_configs
from ..network import HTTPCode
from ..persona_info import PersonaInfo, EnterType
from ..namespace import MessageSource
from ..text_render.text_render import TextRender
from ..response.response import Response
from ..chattts import ChatTTSAPI
from ..special_values import NoGive, nogive, is_no_give
from typing import (
    Iterable,
    Any,
    Callable,
    Awaitable,
    NoReturn,
    TypeVar,
    Type,
    Literal,
    ClassVar,
    overload
)
from .speed_limiter import SpeedLimiter
from .sending_buffer_unit import SendingBufferUnit
from ...exceptions import (
    BreakHandler,
)
from ...logger import logger as base_logger
from .sending_target import SendingTarget
from .text_tender_exceptions import (
    InvalidResponseData,
    RenderResponseException,
    NotInitializedResponse,
    TextRenderException,
)

logger = base_logger.bind(module = "SendMsg")

T_RESPONSE = TypeVar("T_RESPONSE")

SEND_HOOK = Callable[[Message, SendingTarget], Awaitable[None]]

class SendMsg:
    r"""
    Repeater 统一消息发送处理对象

    
    Usage:

        >>> send_msg = SendMsg(
        ...     component = self.component,
        ...     persona_info = PersonaInfo(
        ...         bot = bot,
        ...         event = event,
        ...         args = args
        ...     ),
        ...     matcher = matcher
        ... )
        ...
        >>> # 发送提示信息
        >>> await send_msg.send_prompt(
        ...     message
        ...     continue_handler = True # 使用 continue_handler 保证不中断流程
        ... )
        >>> # 解析一个响应对象，并发送结果
        >>> await send_msg.send_response(
        ...     message
        ...     continue_handler = True
        ... )
        >>> # 发送错误信息
        >>> await send_msg.send_error(
        ...     message # 此处也可以填写异常对象
        ...     continue_handler = True
        ... )
        >>> # 先尝试将错误信息渲染为图片，如果失败再使用文本发送
        >>> await send_msg.send_error_render(
        ...     message, # 此处也可以填写异常对象
        ...     continue_handler = True
        ... )
        >>> # 像 matcher.send() 一样发送消息
        >>> await send_msg.send_any(
        ...     message,
        ...     reply = False, # SendMsg 默认会让消息添加 reply 消息段，可用这种方法将其移除
        ...     continue_handler = True
        ... )
        >>> # 发送一个文件
        >>> await send_msg.send_file(
        ...     file_path,
        ...     continue_handler = True
        ... )
        >>> # 发送一个戳一戳
        >>> await send_msg.send_poke(
        ...     continue_handler = True
        ... )
        >>> 
        >>> # 复制一个输出为 Buffer 的 SendMsg
        >>> copyed_send_msg = send_msg.copy(
        ...     continue_handler = True
        ... )
        >>> # 发送一个消息到缓冲区
        >>> await copyed_send_msg.send_prompt(
        ...     "Test", # 此处也可以填写字符串
        ...     continue_handler = True
        ... )
        >>> # 从缓冲区读取内容
        >>> text_buffer: list[str] = []
        >>> while copyed_send_msg.buffer.qsize() > 0:
        ...     result = await copyed_send_msg.buffer.get()
        ...     text_buffer.append(result.message)
        >>> # 发送一个消息
        >>> await send_msg.send_prompt(
        ...     "\n".join(text_buffer),
        ...     continue_handler = True
        ... )
        >>> 
        >>> # 复制并设置目标为 群聊 1234567890
        >>> copyed_send_msg = send_msg.copy(
        ...     continue_handler = True,
        ...     target_group = "1234567890",
        ...     send_target = SendingTarget.API # 只有设置成 API 才能绕过 Matcher 发送消息
        ... )
        >>> # 发送一个消息到群聊 1234567890
        >>> await copyed_send_msg.send_prompt(
        ...     "Test", # 此处也可以填写字符串
        ...     continue_handler = True
        ... )
        >>> 
        >>> # 复制并设置目标为 用户 1234567890
        >>> copyed_send_msg = send_msg.copy(
        ...     continue_handler = True,
        ...     target_user = "1234567890",
        ...     send_target = SendingTarget.API # 也是只有设置成 API 才能绕过 Matcher 发送消息
        ... )
        >>> # 发送一个消息到用户 1234567890
        >>> await copyed_send_msg.send_prompt(
        ...     "Test", # 此处也可以填写字符串
        ...     continue_handler = True
        ... )
        >>> # 手动退出当前层级 Handler (不终止上层)
        >>> send_msg.break_handler(0) # 可以填写返回值告诉上层自己是否是正常结束
    """
    message_speed_limiter: ClassVar[SpeedLimiter] = SpeedLimiter(
        storage_configs.camouflage.limit_speed_per_minute.send_msg
    )
    file_speed_limiter: ClassVar[SpeedLimiter] = SpeedLimiter(
        storage_configs.camouflage.limit_speed_per_minute.file
    )
    poke_speed_limiter: ClassVar[SpeedLimiter] = SpeedLimiter(
        storage_configs.camouflage.limit_speed_per_minute.poke
    )
    
    @overload
    def __init__(
            self,
            component: str,
            persona_info: PersonaInfo,
            matcher: Type[Matcher],
            reply: MessageSegment | None = None,
            prefix: Message | None = None,
            suffix: Message | None = None,
            target_group: str | None = None,
            target_user: str | None = None,
            send_target: Literal[SendingTarget.MATCHER] = SendingTarget.MATCHER,
            send_hook: SEND_HOOK | None = None,
        ): ...
    
    @overload
    def __init__(
            self,
            component: str,
            persona_info: PersonaInfo,
            matcher: Type[Matcher] | None = None,
            reply: MessageSegment | None = None,
            prefix: Message | None = None,
            suffix: Message | None = None,
            target_group: str | None = None,
            target_user: str | None = None,
            send_target: SendingTarget = SendingTarget.AUTO,
            send_hook: SEND_HOOK | None = None,
        ): ...

    def __init__(
            self,
            component: str,
            persona_info: PersonaInfo,
            matcher: Type[Matcher] | None = None,
            reply: MessageSegment | None = None,
            prefix: Message | None = None,
            suffix: Message | None = None,
            target_group: str | None = None,
            target_user: str | None = None,
            send_target: SendingTarget = SendingTarget.AUTO,
            send_hook: SEND_HOOK | None = None,
        ):
        self._component: str = component
        self._persona_info: PersonaInfo = persona_info
        self._reply: MessageSegment = reply or self._persona_info.reply
        self._prefix: Message = prefix or Message()
        self._suffix: Message = suffix or Message()
        self._chat_tts_api = ChatTTSAPI()
        self._matcher: Type[Matcher] | None = matcher
        self._target_group: str | None = target_group
        self._target_user: str | None = target_user
        self._send_hook: SEND_HOOK | None = send_hook
        
        self._buffer: asyncio.Queue[SendingBufferUnit] = asyncio.Queue()
        self.sending_target: SendingTarget = send_target
        match self.sending_target:
            case SendingTarget.AUTO:
                if matcher is None:
                    self.sending_target = SendingTarget.API
                else:
                    self.sending_target = SendingTarget.MATCHER
            case SendingTarget.MATCHER:
                if matcher is None:
                    raise ValueError("Matcher can't be a target, because it's not given.")

    def __repr__(self) -> str:
        args_map:  list[tuple[str, Any]] = [
            ("component", self._component),
            ("persona_info", self._persona_info),
            ("matcher", self._matcher),
            ("reply", self._reply),
            ("prefix", self._prefix),
            ("suffix", self._suffix),
            ("target_group", self._target_group),
            ("target_user", self._target_user),
            ("sending_target", self.sending_target),
            ("send_hook", self._send_hook)
        ]
        return f"{self.__class__.__name__}({', '.join([f'{k}={v!r}' for k, v in args_map if v is not None])})"
    
    def copy(
            self,
            component: str | NoGive = nogive,
            persona_info: PersonaInfo | NoGive = nogive,
            matcher: Type[Matcher] | None | NoGive = nogive,
            reply: MessageSegment | None | NoGive = nogive,
            prefix: Message | None | NoGive = nogive,
            suffix: Message | None | NoGive = nogive,
            target_group: str | None | NoGive = nogive,
            target_user: str | None | NoGive = nogive,
            send_target: SendingTarget | NoGive = nogive,
            send_hook: SEND_HOOK | None | NoGive = nogive
        ) -> "SendMsg":
        component = component if not is_no_give(component) else self._component
        persona_info = persona_info if not is_no_give(persona_info) else self._persona_info.copy()
        matcher = matcher if not is_no_give(matcher) else self._matcher
        reply = reply if not is_no_give(reply) else self._reply
        prefix = prefix if not is_no_give(prefix) else self._prefix
        suffix = suffix if not is_no_give(suffix) else self._suffix
        send_target = send_target if not is_no_give(send_target) else self.sending_target
        target_group = target_group if not is_no_give(target_group) else self._target_group
        target_user = target_user if not is_no_give(target_user) else self._target_user
        send_hook = send_hook if not is_no_give(send_hook) else self._send_hook

        instance = self.__class__(
            component = component,
            persona_info = persona_info,
            matcher = matcher,
            reply = reply,
            prefix = prefix,
            suffix = suffix,
            target_group = target_group,
            target_user = target_user,
            send_target = send_target,
            send_hook = send_hook
        )
        
        return instance

    def set_prefix(self, prefix: Message):
        """
        设置消息前缀
        """
        if not isinstance(prefix, Message):
            raise TypeError("prefix must be a Message")
        self._prefix = prefix
    
    def add_prefix(self, prefix: MessageSegment | str):
        """
        添加消息前缀
        """
        self._prefix.append(prefix)
    
    def clear_prefix(self):
        """
        清空消息前缀
        """
        self._prefix = Message()

    def set_suffix(self, suffix: Message):
        """
        设置消息后缀
        """
        if not isinstance(suffix, Message):
            raise TypeError("suffix must be a Message")
        self._suffix = suffix

    def add_suffix(self, suffix: MessageSegment | str):
        """
        添加消息后缀
        """
        self._suffix.append(suffix)

    def clear_suffix(self):
        """
        清空消息后缀
        """
        self._suffix = Message()
    
    @overload
    async def __call__(
            self,
            message: str | Message,
            reply: bool = True,
            break_code: int = 0,
            continue_handler: Literal[False] = False,
        ) -> NoReturn: ...
    
    @overload
    async def __call__(
            self,
            message: str | Message,
            reply: bool = True,
            break_code: int = 0,
            continue_handler: Literal[True] = True,
        ) -> None: ...
    
    async def __call__(
            self,
            message: str | Message,
            reply: bool = True,
            break_code: int = 0,
            continue_handler: bool = False,
        ) -> None | NoReturn:
        """
        发送消息
        """
        return await self.send_prompt(
            prompt = message,
            reply = reply,
            break_code = break_code,
            continue_handler = continue_handler,
        )
    
    @property
    def is_debug_mode(self) -> bool:
        """
        是否处于调试模式
        """
        return REPEATER_DEBUG_MODE
    
    @property
    def persona_info(self) -> PersonaInfo:
        """
        当前消息的 PersonaInfo 实例
        """
        return self._persona_info
    
    @property
    def component(self) -> str:
        """
        当前消息的组件
        """
        return self._component
    
    @property
    def matcher(self) -> Type[Matcher] | None:
        """
        当前消息的 Matcher 实例
        """
        return self._matcher
    
    @matcher.setter
    def matcher(self, matcher: Type[Matcher] | None):
        """
        设置当前消息的 Matcher 实例
        """
        if matcher is None:
            self._matcher = None
        elif issubclass(matcher, Matcher):
            self._matcher = matcher
        else:
            raise TypeError(f"matcher must be Matcher or None, not {type(matcher).__name__}")
    
    @property
    def buffer(self) -> asyncio.Queue[SendingBufferUnit]:
        """
        当前消息的缓冲区
        """
        return self._buffer
    
    @buffer.setter
    def buffer(self, buffer: asyncio.Queue[SendingBufferUnit]):
        """
        设置当前消息的缓冲区
        """
        if isinstance(buffer, asyncio.Queue):
            self._buffer = buffer
        else:
            raise TypeError(f"buffer must be asyncio.Queue, not {type(buffer).__name__}")
    
    async def get_hello_content(self) -> str:
        """
        获取每日问候语
        """
        user_configs = await self.persona_info.get_user_configs()
        if user_configs.hello_content is None:
            hello_content_configs = storage_configs.hello_content
        else:
            hello_content_configs = user_configs.hello_content
        
        now = datetime.now()
        buffer: list[str] = [
            hello_content_configs.content
        ]

        suffixs = hello_content_configs.suffixs
        for suffix in suffixs:
            if croniter.match(suffix.cron, now):
                buffer.append(suffix.content)
            
        return "".join(buffer)
    
    @overload
    async def send_debug_mode(
            self,
            reply: bool = True,
            break_code: int = 0,
            continue_handler: Literal[False] = False,
        ) -> NoReturn: ...

    @overload
    async def send_debug_mode(
            self,
            reply: bool = True,
            break_code: int = 0,
            continue_handler: Literal[True] = True,
        ) -> None: ...
    
    async def send_debug_mode(
            self,
            reply: bool = True,
            break_code: int = 0,
            continue_handler: bool = False,
        ) -> NoReturn | None:
        """
        用于调试模式的信息打印

        :param reply: 是否携带引用
        :param break_code: 返回码
        :param continue_handler: 是否继续运行当前处理流程
        """
        logger.info(
            "Send Debug Message"
        )
        await self.send_text(
            f"[{self._component}|{self._persona_info.namespace}|{self._persona_info.nickname}]: {self._persona_info.message}",
            reply = reply,
            break_code = break_code,
            continue_handler = continue_handler,
        )
    
    @overload
    async def send_response_check_code(
            self,
            response: Response[T_RESPONSE],
            message: str | None = None,
            reply: bool = True,
            break_code: int | None = None,
            continue_handler: Literal[False] = False,
        ) -> NoReturn: ...

    @overload
    async def send_response_check_code(
            self,
            response: Response[T_RESPONSE],
            message: str | None = None,
            reply: bool = True,
            break_code: int | None = None,
            continue_handler: Literal[True] = True,
        ) -> None: ...
    
    async def send_response_check_code(
            self,
            response: Response[T_RESPONSE],
            message: str | None = None,
            reply: bool = True,
            break_code: int | None = None,
            continue_handler: bool = False,
        ) -> NoReturn | None:
        """
        发送响应结果并检查状态码

        :param response: 响应体
        :param message: 消息内容，不提供时使用响应体的文本内容
        :param reply: 是否携带引用
        :param break_code: 返回码
        :param continue_handler: 是否继续运行当前处理流程
        """
        logger.info(
            "Send Response Check Code"
        )
        logger.info(
            "Response Code Is {code}",
            code = response.code
        )
        if response.code != 200:
            if break_code is None:
                break_code = 1
            await self.send_error_response(
                response = response,
                message = message,
                reply = reply,
                break_code = break_code,
                continue_handler = continue_handler,
            )
        else:
            if break_code is None:
                break_code = 0
            await self.send_response(
                response = response,
                message = message,
                reply = reply,
                break_code = break_code,
                continue_handler = continue_handler,
            )
    
    @overload
    async def send_error_response(
            self,
            response: Response[T_RESPONSE],
            message: str | None = None,
            reply: bool = True,
            break_code: int = 1,
            continue_handler: Literal[False] = False,
        ) -> NoReturn: ...

    @overload
    async def send_error_response(
            self,
            response: Response[T_RESPONSE],
            message: str | None = None,
            reply: bool = True,
            break_code: int = 1,
            continue_handler: Literal[True] = True,
        ) -> None: ...
    
    async def send_error_response(
            self,
            response: Response[T_RESPONSE],
            message: str | None = None,
            reply: bool = True,
            break_code: int = 1,
            continue_handler: bool = False,
        ) -> NoReturn | None:
            """
            发送响应对象中的报错信息

            :param response: 响应对象
            :param message: 自定义消息文本或解析处理函数
            :param reply: 是否携带引用
            :param break_code: 返回码
            :param continue_handler: 是否继续运行当前处理流程
            """
            logger.info(
                "Send Error Response"
            )
            await self.send_error_render(
                response if message is None else message,
                get_error_response = True,
                reply = reply,
                break_code = break_code,
                continue_handler = continue_handler
            )
            
    @overload
    async def send_response(
            self,
            response: Response[T_RESPONSE],
            message: Callable[[Response[T_RESPONSE]], str] | str | None = None,
            reply: bool = True,
            break_code: int = 0,
            continue_handler: Literal[False] = False,
        ) -> NoReturn: ...

    @overload
    async def send_response(
            self,
            response: Response[T_RESPONSE],
            message: Callable[[Response[T_RESPONSE]], str] | str | None = None,
            reply: bool = True,
            break_code: int = 0,
            continue_handler: Literal[True] = True,
        ) -> None: ...
    
    async def send_response(
            self,
            response: Response[T_RESPONSE],
            message: Callable[[Response[T_RESPONSE]], str] | str | None = None,
            reply: bool = True,
            break_code: int = 0,
            continue_handler: bool = False,
        ) -> NoReturn | None:
        """
        发送响应对象中的内容，主要用于HTTP错误提示

        :param response: 响应对象
        :param message: 自定义消息文本或解析处理函数
        :param reply: 是否携带引用
        :param break_code: 返回码
        :param continue_handler: 是否继续运行当前处理流程
        """
        logger.info(
            "Send Response"
        )

        if callable(message):
            message = message(response)
        elif isinstance(message, str):
            message = message
        else:
            message = response.text
        
        await self.send_http_status(
            http_status = response.code,
            message = message,
            reply = reply,
            break_code = break_code,
            continue_handler = continue_handler,
        )
    
    @overload
    async def send_http_status(
            self,
            http_status: int,
            message: str | None = None,
            reply: bool = True,
            break_code: int | None = None,
            continue_handler: Literal[False] = False,
        ) -> NoReturn: ...

    @overload
    async def send_http_status(
            self,
            http_status: int,
            message: str | None = None,
            reply: bool = True,
            break_code: int | None = None,
            continue_handler: Literal[True] = True,
        ) -> None: ...
    
    async def send_http_status(
            self,
            http_status: int,
            message: str | None = None,
            reply: bool = True,
            break_code: int | None = None,
            continue_handler: bool = False,
        ) -> NoReturn | None:
        """
        发送 HTTP 状态码，用于提示 HTTP 错误

        :param http_status: HTTP 状态码
        :param message: 消息文本
        :param reply: 是否携带引用
        :param break_code: 返回码
        :param continue_handler: 是否继续运行当前处理流程
        """
        logger.info(
            "Send HTTP Status"
        )

        if break_code is None:
            if http_status == 200:
                break_code = 0
            else:
                break_code = 1

        await self.send_prompt(
            (
                f"{message}\n"
                f"HTTP Code: {http_status}({HTTPCode(code=http_status)})"
            ),
            reply = reply,
            break_code = break_code,
            continue_handler = continue_handler
        )
    
    @overload
    async def send_multiple_responses(
            self,
            *responses: Response[T_RESPONSE] | tuple[Response[T_RESPONSE], str],
            reply: bool = True,
            break_code: int | None = None,
            continue_handler: Literal[False] = False
        ) -> NoReturn: ...
    
    @overload
    async def send_multiple_responses(
            self,
            *responses: Response[T_RESPONSE] | tuple[Response[T_RESPONSE], str],
            reply: bool = True,
            break_code: int | None = None,
            continue_handler: Literal[True] = True
        ) -> None: ...
    
    async def send_multiple_responses(
            self,
            *responses: Response[T_RESPONSE] | tuple[Response[T_RESPONSE], str],
            reply: bool = True,
            break_code: int | None = None,
            continue_handler: bool = False,
        ) -> NoReturn | None:
        """
        发送多个响应对象中的内容

        :param responses: 响应对象
        :param reply: 是否携带引用
        :param break_code: 返回码
        :param continue_handler: 是否继续运行当前处理流程
        """
        logger.info(
            "Send Multiple Responses"
        )
        text_buffer: list[str] = []
        failed: int = 0
        for index, response in enumerate(responses, start=1):
            if isinstance(response, tuple):
                text_buffer.append(f"[{response[1]}] HTTP Code: {response[0].code}({HTTPCode(response[0].code)})")
                if response[0].code != 200:
                    failed += 1
            elif isinstance(response, Response):
                text_buffer.append(f"[{index}] HTTP Code: {response.code}({HTTPCode(response.code)})")
                if response.code != 200:
                    failed += 1
            else:
                raise TypeError(f"Unsupported type: {type(response)}")
        
        if failed == 0:
            if break_code is None:
                break_code = 0
            text_buffer.append("All requests are successful.")
        else:
            if break_code is None:
                break_code = 1
            text_buffer.append(f"{failed} requests failed.")
        
        await self.send_prompt(
            "\n".join(text_buffer),
            reply = reply,
            break_code = break_code,
            continue_handler = continue_handler
        )
    
    @overload
    async def send_hello(
            self,
            reply: bool = True,
            break_code: int = 0,
            continue_handler: Literal[False] = False,
        ) -> NoReturn: ...
    
    @overload
    async def send_hello(
            self,
            reply: bool = True,
            break_code: int = 0,
            continue_handler: Literal[True] = True,
        ) -> None: ...
    
    async def send_hello(
            self,
            reply: bool = True,
            break_code: int = 0,
            continue_handler: bool = False,
        ) -> NoReturn | None:
        """
        发送欢迎信息

        :param reply: 是否携带引用
        :param break_code: 返回码
        :param continue_handler: 是否继续运行当前处理流程
        """
        logger.info(
            "Send Hello Message"
        )
        hello_content = await self.get_hello_content()
        await self.send_text(
            hello_content,
            reply = reply,
            break_code = break_code,
            continue_handler = continue_handler
        )
    
    @property
    def prompt_prefix(self) -> str:
        """
        提示前缀
        """
        return (
            f"== {self._component} ==\n"
            f"> [{self._persona_info.namespace}|{str(datetime.now().isoformat())}]\n"
            f"> [Task: {self._persona_info.task_id}]\n"
        )
    
    @overload
    async def send_prompt(
            self,
            prompt: Message | str,
            reply: bool = True,
            break_code: int = 0,
            continue_handler: Literal[False] = False,
        ) -> NoReturn: ...

    @overload
    async def send_prompt(
            self,
            prompt: Message | str,
            reply: bool = True,
            break_code: int = 0,
            continue_handler: Literal[True] = True,
        ) -> None: ...
    
    async def send_prompt(
            self,
            prompt: Message | str,
            reply: bool = True,
            break_code: int = 0,
            continue_handler: bool = False
        ) -> NoReturn | None:
        """
        发送提示信息

        :param prompt: 提示信息
        :param reply: 是否携带引用
        :param break_code: 返回码
        :param continue_handler: 是否继续运行当前处理流程
        """
        logger.info(
            "Send Prompt"
        )
        if isinstance(prompt, Message):
            await self._send(
                Message(
                    MessageSegment.text(
                        self.prompt_prefix
                    ),
                ).extend(prompt),
                reply = reply,
                break_code = break_code,
                continue_handler = continue_handler
            )
        elif isinstance(prompt, str):
            await self._send(
                self.prompt_prefix + prompt,
                reply = reply,
                break_code = break_code,
                continue_handler = continue_handler
            )
        else:
            raise TypeError("prompt must be str or Message")
    
    @overload
    async def send_error(
            self,
            error: str | BaseException,
            reply: bool = True,
            break_code: int = 1,
            continue_handler: Literal[False] = False,
        ) -> NoReturn: ...

    @overload
    async def send_error(
            self,
            error: str | BaseException,
            reply: bool = True,
            break_code: int = 1,
            continue_handler: Literal[True] = True,
        ) -> None: ...
    
    async def send_error(
            self,
            error: str | BaseException,
            reply: bool = True,
            break_code: int = 1,
            continue_handler: bool = False
        ) -> NoReturn | None:
        """
        发送错误信息

        :param error: 错误信息
        :param reply: 是否携带引用
        :param break_code: 返回码
        :param continue_handler: 是否继续运行当前处理流程
        """
        logger.info(
            "Send Error"
        )
        if isinstance(error, BaseException):
            await self.send_prompt(
                (
                    f"{error.__class__.__name__}: {error}"
                ),
                reply = reply,
                break_code = break_code,
                continue_handler = continue_handler
            )
        else:
            await self.send_prompt(
                (
                    f"Error: {error}"
                ),
                reply = reply,
                break_code = break_code,
                continue_handler = continue_handler
            )
    
    @overload
    async def send_warning(
            self,
            warning: str,
            reply: bool = True,
            break_code: int = 2,
            continue_handler: Literal[True] = True
        ) -> None: ...

    @overload
    async def send_warning(
            self,
            warning: str,
            reply: bool = True,
            break_code: int = 2,
            continue_handler: Literal[False] = False
        ) -> NoReturn: ...
    
    async def send_warning(
            self,
            warning: str,
            reply: bool = True,
            break_code: int = 2,
            continue_handler: bool = True
        ) -> NoReturn | None:
        """
        发送警告信息

        :param warning: 警告信息
        :param reply: 是否携带引用
        :param break_code: 返回码
        :param continue_handler: 是否继续运行当前处理流程
        """
        logger.info(
            "Send Warning"
        )
        await self.send_prompt(
            (
                f"Warning: {warning}"
            ),
            reply = reply,
            break_code = break_code,
            continue_handler = continue_handler
        )
    
    @overload
    async def send_text(
            self,
            text: str,
            reply: bool = True,
            break_code: int = 0,
            continue_handler: Literal[False] = False
        ) -> NoReturn: ...
    
    @overload
    async def send_text(
            self,
            text: str,
            reply: bool = True,
            break_code: int = 0,
            continue_handler: Literal[True] = True
        ) -> None: ...
    
    async def send_text(
            self,
            text: str,
            reply: bool = True,
            break_code: int = 0,
            continue_handler: bool = False
        ) -> NoReturn | None:
        """
        发送纯文本

        :param text: 文本内容
        :param reply: 是否携带引用
        :param break_code: 返回码
        :param continue_handler: 是否继续运行当前处理流程
        """
        logger.info(
            "Send Text"
        )
        await self._send(
            Message(
                MessageSegment.text(
                    text
                )
            ),
            reply = reply,
            break_code = break_code,
            continue_handler = continue_handler
        )
    
    @overload
    async def send_cq_text(
            self,
            text: str,
            reply: bool = True,
            break_code: int = 0,
            continue_handler: Literal[False] = False
        ) -> NoReturn: ...
    
    @overload
    async def send_cq_text(
            self,
            text: str,
            reply: bool = True,
            break_code: int = 0,
            continue_handler: Literal[True] = True
        ) -> None: ...
    
    async def send_cq_text(
            self,
            text: str,
            reply: bool = True,
            break_code: int = 0,
            continue_handler: bool = False
        ) -> NoReturn | None:
        """
        发送纯文本

        :param text: CQ 码文本内容
        :param reply: 是否携带引用
        :param continue_handler: 是否继续运行当前处理流程
        """
        logger.info(
            "Send CQ Text"
        )
        await self._send(
            Message(
                text
            ),
            reply = reply,
            break_code = break_code,
            continue_handler = continue_handler
        )
    
    @overload
    async def send_mixed_render(
            self,
            text_to_render: str | Message,
            prefix_text: str | None = None,
            suffix_text: str | None = None,
            prompt_mode: bool = True,
            document_bottom_comment: str = "",
            reply: bool = True,
            break_code: int = 0,
            continue_handler: Literal[False] = False
        ) -> NoReturn: ...
    
    @overload
    async def send_mixed_render(
            self,
            text_to_render: str | Message,
            prefix_text: str | None = None,
            suffix_text: str | None = None,
            prompt_mode: bool = True,
            document_bottom_comment: str = "",
            reply: bool = True,
            break_code: int = 0,
            continue_handler: Literal[True] = True
        ) -> None: ...
    
    async def send_mixed_render(
            self,
            text_to_render: str | Message,
            prefix_text: str | None = None,
            suffix_text: str | None = None,
            prompt_mode: bool = True,
            document_bottom_comment: str = "",
            reply: bool = True,
            break_code: int = 0,
            continue_handler: bool = False
        ) -> NoReturn | None:
        """
        发送混合渲染文本

        :param prefix_text: 前缀文本内容
        :param text_to_render: 需要渲染的文本内容
        :param suffix_text: 后缀文本内容
        :param reply: 是否携带引用
        :param continue_handler: 是否继续运行当前处理流程
        """
        logger.info(
            "Send Mixed Render"
        )
        image = await self.render_text_to_msg_segment(
            text_to_render,
            document_bottom_comment = document_bottom_comment
        )
        message = Message()

        if prefix_text:
            message.append(prefix_text)

        message.append(image)

        if suffix_text:
            message.append(suffix_text)
        
        if prompt_mode:
            await self.send_prompt(
                message,
                reply=reply,
                continue_handler = continue_handler
            )
        else:
            await self._send(
                message,
                reply = reply,
                break_code = break_code,
                continue_handler = continue_handler
            )
    
    @overload
    async def send_multiple_render(
            self,
            messages: Iterable[str | Message],
            document_bottom_comment: str = "",
            reply: bool = False,
            break_code: int = 0,
            continue_handler: Literal[False] = False
        ) -> NoReturn: ...

    @overload
    async def send_multiple_render(
            self,
            messages: Iterable[str | Message],
            document_bottom_comment: str = "",
            reply: bool = False,
            break_code: int = 0,
            continue_handler: Literal[True] = True
        ) -> None: ...
    
    async def send_multiple_render(
            self,
            messages: Iterable[str | Message],
            document_bottom_comment: str = "",
            reply: bool = True,
            break_code: int = 0,
            continue_handler: bool = False
        ) -> NoReturn | None:
        """
        发送多个渲染文本

        :param messages: 待发送的消息
        :param document_bottom_comment: 文档底部注释
        :param reply: 是否回复
        :param continue_handler: 是否继续
        """
        logger.info(
            "Send Multiple Render"
        )
        tasks: list[asyncio.Task[MessageSegment]] = []
        for msg in messages:
            tasks.append(
                asyncio.create_task(
                    self.render_text_to_msg_segment(
                        msg,
                        document_bottom_comment = document_bottom_comment
                    )
                )
            )
        
        results = await asyncio.gather(*tasks)
        message = Message(results)
        
        await self._send(
            message,
            reply = reply,
            break_code = break_code,
            continue_handler = continue_handler
        )
    
    @overload
    async def send_render_prompt(
            self,
            text: str | Message,
            document_bottom_comment: str = "",
            reply: bool = True,
            break_code: int = 0,
            continue_handler: Literal[False] = False
        ) -> NoReturn: ...
    
    @overload
    async def send_render_prompt(
            self,
            text: str | Message,
            document_bottom_comment: str = "",
            reply: bool = True,
            break_code: int = 0,
            continue_handler: Literal[True] = True
        ) -> None: ...
    
    async def send_render_prompt(
            self,
            text: str | Message,
            document_bottom_comment: str = "",
            reply: bool = True,
            break_code: int = 0,
            continue_handler: bool = False
        ) -> NoReturn | None:
        """
        发送提示消息（渲染为图片）

        :param text: 提示消息
        :param document_bottom_comment: 文档底部注释
        :param reply: 是否回复
        :param continue_handler: 是否继续处理
        """
        logger.info(
            "Send Render Prompt"
        )
        image = await self.render_text_to_msg_segment(
            text,
            document_bottom_comment = document_bottom_comment
        )
        await self._send(
            Message(
                [
                    MessageSegment.text(self.prompt_prefix),
                    image
                ]
            ),
            reply = reply,
            break_code = break_code,
            continue_handler = continue_handler
        )
    
    @overload
    async def send_render(
            self,
            text: str | Message,
            document_bottom_comment: str = "",
            reply: bool = True,
            break_code: int = 0,
            continue_handler: Literal[True] = True
        ) -> None: ...
    
    @overload
    async def send_render(
            self,
            text: str | Message,
            document_bottom_comment: str = "",
            reply: bool = True,
            break_code: int = 0,
            continue_handler: Literal[False] = False
        ) -> NoReturn: ...
    
    async def send_render(
            self,
            text: str | Message,
            document_bottom_comment: str = "",
            reply: bool = True,
            break_code: int = 0,
            continue_handler: bool = False
        ) -> NoReturn | None:
        """
        发送渲染后的文本

        :param text: 渲染文本内容
        :param document_bottom_comment: 文档底部注释
        :param reply: 是否携带引用
        :param continue_handler: 是否继续运行当前处理流程
        """
        logger.info(
            "Send Render"
        )
        image = await self.render_text_to_msg_segment(
            text,
            document_bottom_comment = document_bottom_comment
        )
        await self._send(
            Message(image),
            reply = reply,
            break_code = break_code,
            continue_handler = continue_handler
        )
    
    @overload
    async def send_tts(
            self,
            text: str,
            send_error_message: bool = True,
            reply: bool = False,
            break_code: int = 0,
            continue_handler: Literal[False] = False
        ) -> NoReturn: ...

    @overload
    async def send_tts(
            self,
            text: str,
            send_error_message: bool = True,
            reply: bool = False,
            break_code: int = 0,
            continue_handler: Literal[True] = True
        ) -> None: ...
    
    async def send_tts(
            self,
            text: str,
            send_error_message: bool = True,
            reply: bool = False,
            break_code: int = 0,
            continue_handler: bool = False
        ) -> NoReturn | None:
        """
        发送tts

        :param text: 文本
        :param send_error_message: 是否发送错误信息
        :param reply: 是否回复
        :param continue_handler: 是否继续处理流程
        """
        logger.info(
            "Send TTS"
        )
        response = await self._chat_tts_api.text_to_speech(text)
        if response.code == 200:
            data = response.get_data()
            if data is not None:
                await self._send(
                    message = MessageSegment.record(data.audio_files[0].url),
                    reply = reply,
                    break_code = break_code,
                    continue_handler = continue_handler
                )
        elif send_error_message:
            await self.send_response(response, message = "TTS Error.")
        else:
            logger.error(f"Send TTS Error: {response.code} {response.text}")

    @overload
    async def send_error_render(
            self,
            *errors: str | Message | Exception | Response,
            threshold: float | None = None,
            get_error_response: bool = False,
            document_bottom_comment: str = "",
            reply: bool = True,
            break_code: int = 1,
            continue_handler: Literal[False] = False
        ) -> NoReturn: ...

    @overload
    async def send_error_render(
            self,
            *errors: str | Message | Exception | Response,
            threshold: float | None = None,
            get_error_response: bool = False,
            document_bottom_comment: str = "",
            reply: bool = True,
            break_code: int = 1,
            continue_handler: Literal[True] = True
        ) -> None: ...

    async def send_error_render(
            self,
            *errors: str | Message | Exception | Response,
            threshold: float | None = None,
            get_error_response: bool = False,
            document_bottom_comment: str = "",
            reply: bool = True,
            break_code: int = 1,
            continue_handler: bool = False
        ) -> None | NoReturn:
        """
        发送错误渲染

        :param errors: 错误信息
        :param threshold: 长度阈值
        :param document_bottom_comment: 文档底部注释
        :param reply: 是否回复
        :param continue_handler: 是否继续处理流程
        """
        logger.info(
            "Send Error Render"
        )
        texts: list[str] = []
        for error in errors:
            if isinstance(error, str):
                texts.append(error)
            elif isinstance(error, Message):
                texts.append(error.extract_plain_text())
            elif isinstance(error, Exception):
                texts.append(f"Source Exception: {error.__class__.__name__}\nException Message: {str(error)}")
            elif isinstance(error, Response):
                if get_error_response:
                    error_response = error.get_error()
                    if error_response is not None:
                        message = f"Error Message: {error_response.error_message}\nSource Exception: {error_response.source_exception}\nException Message: {error_response.exception_message}"
                    elif error.text:
                        message = error.text
                    else:
                        message = f"[Error Info Is Invalid]"
                    texts.append(message)
                else:
                    texts.append(f"HTTP Code: {error.code}{HTTPCode(error.code).message})\nException Message: {error.text}")

        text = "\n".join(texts)
        length_score = self.text_length_score(text)
        logger.info(
            "Text Length Score: {length_score}",
            length_score = length_score
        )
    
        message = Message()

        if threshold is None:
            threshold = self.length_score_threshold

        if length_score >= threshold:
            try:
                image = await self.render_text_to_msg_segment(
                    text,
                    document_bottom_comment = document_bottom_comment,
                    style = storage_configs.render_error_message.style,
                    html_template = storage_configs.render_error_message.html_template,
                    title = storage_configs.render_error_message.title
                )
                message.append(image)
            except TextRenderException as e:
                logger.error(
                    "Render Error Message Failed: {exc_info}",
                    exc_info = e
                )
                message.append(MessageSegment.text(text))
        else:
            message.append(MessageSegment.text(text))

        await self.send_prompt(
            message,
            reply = reply,
            break_code = break_code,
            continue_handler = continue_handler
        )

    @property
    def length_score_threshold(self) -> float:
        match self._persona_info.source:
            case MessageSource.GROUP:
                return storage_configs.text_length_score_configs.threshold.group
            case MessageSource.PRIVATE:
                return storage_configs.text_length_score_configs.threshold.private

        raise ValueError(f"Invalid source: {self._persona_info.source}")
    
    @overload
    async def send_check_length(
            self,
            message: Message | str,
            threshold: float | None = None,
            document_bottom_comment: str = "",
            reply: bool = True,
            break_code: int = 0,
            continue_handler: Literal[False] = False
        ) -> NoReturn: ...
    
    @overload
    async def send_check_length(
            self,
            message: Message | str,
            threshold: float | None = None,
            document_bottom_comment: str = "",
            reply: bool = True,
            break_code: int = 0,
            continue_handler: Literal[True] = True
        ) -> None: ...
    
    async def send_check_length(
            self,
            message: Message | str,
            threshold: float | None = None,
            document_bottom_comment: str = "",
            reply: bool = True,
            break_code: int = 0,
            continue_handler: bool = False
        ) -> NoReturn | None:
        """
        发送长度检测后的文本

        :param message: 消息
        :param threshold: 长度阈值
        :param document_bottom_comment: 文档底部注释
        :param reply: 是否回复
        :param break_code: 返回码
        :param continue_handler: 是否继续处理流程
        """
        logger.info(
            "Send Check Length"
        )
        if isinstance(message, Message):
            text = message.extract_plain_text()
        elif isinstance(message, str):
            text = message
        else:
            raise TypeError(f"message must be Message or str, but got {type(message)}")
        
        if threshold is None:
            threshold = self.length_score_threshold
        
        length_score = self.text_length_score(text)
        if length_score >= threshold:
            await self.send_render(
                text,
                document_bottom_comment = document_bottom_comment,
                reply = reply,
                break_code = break_code,
                continue_handler = continue_handler
            )
        else:
            await self.send_text(
                text,
                reply = reply,
                break_code = break_code,
                continue_handler = continue_handler
            )
    
    @overload
    async def send_check_length_prompt(
            self,
            prompt: Message | str,
            threshold: float | None = None,
            document_bottom_comments: str = "",
            reply: bool = True,
            break_code: int = 0,
            continue_handler: Literal[False] = False
        ) -> NoReturn: ...
    
    @overload
    async def send_check_length_prompt(
            self,
            prompt: Message | str,
            threshold: float | None = None,
            document_bottom_comments: str = "",
            reply: bool = True,
            break_code: int = 0,
            continue_handler: Literal[True] = True
        ) -> None: ...
    
    async def send_check_length_prompt(
            self,
            prompt: Message | str,
            threshold: float | None = None,
            document_bottom_comments: str = "",
            reply: bool = True,
            break_code: int = 0,
            continue_handler: bool = False
        ) -> NoReturn | None:
        """
        发送提示消息并检查长度

        :param prompt: 提示消息
        :param threshold: 长度阈值
        :param document_bottom_comment: 文档底部注释
        :param reply: 是否回复
        :param break_code: 返回码
        :param continue_handler: 是否继续处理
        """
        logger.info(
            "Send Check Length Prompt"
        )
        if isinstance(prompt, Message):
            text = prompt.extract_plain_text()
        elif isinstance(prompt, str):
            text = prompt
        else:
            raise TypeError(f"message must be Message or str, but got {type(prompt)}")

        if threshold is None:
            threshold = self.length_score_threshold
    
        length_score = self.text_length_score(text)
        if length_score >= threshold:
            await self.send_mixed_render(
                text,
                document_bottom_comment = document_bottom_comments,
                reply = reply,
                prompt_mode = True,
                break_code = break_code,
                continue_handler = continue_handler
            )
        else:
            await self.send_prompt(
                text,
                reply = reply,
                break_code = break_code,
                continue_handler = continue_handler
            )
    
    @staticmethod
    async def empty_message() -> MessageSegment:
        """
        在发送聊天响应时，消息为空的提示

        :return: 空消息
        """
        return MessageSegment.text("[Message is empty.]")
    
    @staticmethod
    async def _get_text_message(content: str) -> MessageSegment:
        """
        获取文本消息

        :param content: 文本内容
        :return: 文本消息
        """
        return MessageSegment.text(content)
    
    @overload
    async def send_chat_response(
            self,
            reasoning_content: str | None = None,
            tools_content: str | None = None,
            content: str = "",
            reply: bool = True,
            break_code: int = 0,
            continue_handler: Literal[False] = False
        ) -> NoReturn: ...
    
    @overload
    async def send_chat_response(
            self,
            reasoning_content: str | None = None,
            tools_content: str | None = None,
            content: str = "",
            reply: bool = True,
            break_code: int = 0,
            continue_handler: Literal[True] = True
        ) -> None: ...
    
    async def send_chat_response(
            self,
            reasoning_content: str | None = None,
            tools_content: str | None = None,
            content: str = "",
            reply: bool = True,
            break_code: int = 0,
            continue_handler: bool = False
        ) -> NoReturn | None:
        """
        发送聊天响应

        :param reasoning_content: 推理内容
        :param tools_content: 工具内容
        :param content: 文本内容
        :param reply: 是否回复
        :param break_code: 返回码
        :param continue_handler: 是否继续处理
        """
        logger.info(
            "Send Chat Response"
        )
        tasks: list[asyncio.Task[MessageSegment]] = []
        if reasoning_content:
            tasks.append(
                asyncio.create_task(
                    self.render_text_to_msg_segment(
                        reasoning_content,
                    )
                )
            )

        if tools_content:
            tasks.append(
                asyncio.create_task(
                    self.render_text_to_msg_segment(
                        tools_content,
                    )
                )
            )
        
        if content:
            if self.text_length_score(content) >= self.text_length_score_threshold:
                tasks.append(
                    asyncio.create_task(
                        self.render_text_to_msg_segment(
                            content,
                        )
                    )
                )
            else:
                
                tasks.append(
                    asyncio.create_task(
                        self._get_text_message(content)
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

        await self._send(
            message,
            reply=reply,
            break_code=break_code,
            continue_handler = continue_handler
        )
    
    @overload
    async def send_images(
            self,
            *images: str | bytes | BytesIO | Path,
            reply: bool = True,
            break_code: int = 0,
            continue_handler: Literal[False] = False
        ) -> NoReturn: ...
    
    @overload
    async def send_images(
            self,
            *images: str | bytes | BytesIO | Path,
            reply: bool = True,
            break_code: int = 0,
            continue_handler: Literal[True] = True
        ) -> None: ...
    
    async def send_images(
            self,
            *images: str | bytes | BytesIO | Path,
            reply: bool = True,
            break_code: int = 0,
            continue_handler: bool = False
        ) -> NoReturn | None:
        """
        发送图片

        :param images: 图片
        :param reply: 是否回复
        :param break_code: 返回码
        :param continue_handler: 是否继续处理
        """
        logger.info(
            "Send Images"
        )
        message = Message()
        for image in images:
            message.append(
                MessageSegment.image(image)
            )

        await self._send(
            message,
            reply=reply,
            break_code=break_code,
            continue_handler = continue_handler
        )
    
    @overload
    async def send_any(
            self,
            message: str | Message | MessageSegment,
            reply: bool = True,
            break_code: int = 0,
            continue_handler: Literal[False] = False
        ) -> NoReturn: ...

    @overload
    async def send_any(
            self,
            message: str | Message | MessageSegment,
            reply: bool = True,
            break_code: int = 0,
            continue_handler: Literal[True] = True
        ) -> None: ...
    
    async def send_any(
            self,
            message: str | Message | MessageSegment,
            reply: bool = True,
            break_code: int = 0,
            continue_handler: bool = False
        ) -> NoReturn | None:
        """
        发送任意消息

        :param message: 消息对象
        :param reply: 是否携带引用
        :param break_code: 返回值
        :param continue_handler: 是否继续运行当前处理流程
        """
        logger.info(
            "Send Any"
        )
        await self._send(
            message,
            reply=reply,
            break_code=break_code,
            continue_handler = continue_handler
        )

    @staticmethod
    def handler_finished() -> NoReturn:
        """
        跳出当前处理函数

        :raise: FinishedException
        """
        logger.info(
            "Handler finished"
        )
        raise FinishedException

    @staticmethod
    def break_handler(code: int = 0) -> NoReturn:
        """
        跳出当前处理函数

        :raise: BreakHandler
        """
        logger.info(
            "Break handler"
        )
        raise BreakHandler(code)
    
    async def render_text_to_msg_segment(
        self,
        message: str | Message,
        style: str | None = None,
        image_expiry_time: int | None = None,
        html_template: str | None = None,
        title: str | None = None,
        document_bottom_comment: str | None = None,
        width: int | None = None,
        height: int | None = None,
        direct_output: bool | None = None,
        no_pre_labels: bool | None = None,
        no_escape: bool | None = None,
        quality: int | None = None
    ) -> MessageSegment:
        """
        渲染文本
        :param message: 渲染内容
        :param style: 渲染样式
        :param image_expiry_time: 图片过期时间
        :param html_template: HTML 模板
        :param title: 文档标题
        :param document_bottom_comment: 文档底部注释
        :param width: 图片宽度
        :param height: 图片高度
        :param direct_output: 是否直接输出
        :param no_pre_labels: 是否不添加标签
        :param no_escape: 是否不转义
        :param quality: 图片质量
        :return: 渲染图片的 MessageSegment
        """
        logger.info(
            "Render Text to Msg Segment"
        )

        texts: list[str] = []
        if isinstance(message, str):
            texts.append(message)
        elif isinstance(message, Message):
            for segment in message:
                if segment.type == "text":
                    texts.append(
                        segment.data["text"]
                    )
                elif segment.type == "image":
                    texts.append(
                        f"![{segment.data['file']}]({segment.data['url']})"
                    )
        else:
            raise TypeError("message must be str or Message")
        
        return MessageSegment.image(
            await self.render_text(
                text = "".join(texts),
                style = style,
                image_expiry_time = image_expiry_time,
                html_template = html_template,
                title = title,
                document_bottom_comment = document_bottom_comment,
                width = width,
                height = height,
                direct_output = direct_output,
                no_pre_labels = no_pre_labels,
                no_escape = no_escape,
                quality = quality
            )
        )

    async def render_text(
        self,
        text: str,
        style: str | None = None,
        image_expiry_time: int | None = None,
        html_template: str | None = None,
        title: str | None = None,
        document_bottom_comment: str | None = None,
        width: int | None = None,
        height: int | None = None,
        direct_output: bool | None = None,
        no_pre_labels: bool | None = None,
        no_escape: bool | None = None,
        quality: int | None = None
    ) -> str:
        """
        渲染文本

        :param text: 渲染文本内容
        :param style: 渲染样式
        :param image_expiry_time: 图片过期时间
        :param html_template: HTML 模板
        :param title: 文档标题
        :param document_bottom_comment: 文档底部注释
        :param width: 图片宽度
        :param height: 图片高度
        :param direct_output: 是否直接输出
        :param no_pre_labels: 是否不添加标签
        :param no_escape: 是否不转义
        :param quality: 图片质量
        :return: 渲染图片的 URL
        """
        logger.info(
            "Render Text:\n{text}",
            text = text,
        )
        user_configs = await self.persona_info.get_user_configs()
        text_render = TextRender(
            persona_info = self.persona_info,
            user_configs = user_configs,
        )
        if text:
            render_response: Response[RendedImage] = await text_render.render(
                text = text,
                style = style,
                image_expiry_time = image_expiry_time,
                html_template = html_template,
                title = title,
                document_bottom_comment = document_bottom_comment,
                width = width,
                height = height,
                direct_output = direct_output,
                no_pre_labels = no_pre_labels,
                no_escape = no_escape,
                quality = quality
            )
            if render_response:
                data = render_response.get_data()
                if data is not None:
                    url = data.image_url
                    return url
                else:
                    logger.error(f"Render Data Is Invalid")
                    raise InvalidResponseData(render_response)
            elif render_response.initialized:
                raise NotInitializedResponse(render_response)
            else:
                raise RenderResponseException(render_response)
        else:
            raise ValueError("Text is empty.")
    
    @overload
    async def _send(
            self,
            message: str | Message | MessageSegment,
            reply: bool = True,
            break_code: int = 0,
            continue_handler: Literal[False] = False
        ) -> NoReturn: ...
    
    @overload
    async def _send(
            self,
            message: str | Message | MessageSegment,
            reply: bool = True,
            break_code: int = 0,
            continue_handler: Literal[True] = True
        ) -> None: ...
    
    async def _send(
            self,
            message: str | Message | MessageSegment,
            reply: bool = True,
            break_code: int = 0,
            continue_handler: bool = False
        ) -> NoReturn | None:
        """
        发送消息

        :param message: 消息对象
        :param reply: 是否携带引用
        :param continue_handler: 是否继续运行当前处理流程
        """
        send_msg = self._prefix + message + self._suffix

        if self._persona_info.enter_type != EnterType.External and reply:
            send_msg = self._reply + send_msg

        if self._send_hook is not None:
            await self._send_hook(
                send_msg,
                self.sending_target
            )
        
        try:
            await self._send_to_target(
                message = send_msg,
                reply = reply,
                break_code = break_code,
                continue_handler = continue_handler
            )
        except Exception as error:
            logger.error(
                "Message Send Failed: \n{error}",
                error = error
            )
            raise
        if not continue_handler:
            self.break_handler(break_code)
    
    async def _send_to_target(
        self,
        message: str | Message | MessageSegment,
        reply: bool = True,
        break_code: int = 0,
        continue_handler: bool = False,
        *args,
        **kwargs
    ) -> None:
        """
        发送消息到目标

        :param message: 消息对象
        """
        match self.sending_target:
            case SendingTarget.BUFFER:
                logger.info(
                    "Send to buffer: \n{message}",
                    message = message
                )
                await self._send_to_queue(
                    message,
                    reply = reply,
                    break_code = break_code,
                    continue_handler = continue_handler,
                    *args,
                    **kwargs
                )
            case SendingTarget.MATCHER:
                logger.info(
                    "Send to matcher: \n{message}",
                    message = message
                )
                await self.message_speed_limiter.submit(
                    task = self._send_to_matcher(
                        message,
                        reply = reply,
                        break_code = break_code,
                        continue_handler = continue_handler,
                        *args,
                        **kwargs
                    )
                )
            case SendingTarget.API:
                logger.info(
                    "Send to api: \n{message}",
                    message = message
                )
                await self.message_speed_limiter.submit(
                    task = self._send_to_api(
                        message,
                        reply = reply,
                        break_code = break_code,
                        continue_handler = continue_handler,
                        *args,
                        **kwargs
                    )
                )    
            case SendingTarget.NULL:
                logger.info(
                    "Send to null: \n{message}",
                    message = message
                )
                pass
    
    async def _send_to_queue(
        self,
        message: str | Message | MessageSegment,
        reply: bool = True,
        break_code: int = 0,
        continue_handler: bool = False,
        *args,
        **kwargs
    ) -> None:
        """
        发送消息到队列

        :param message: 消息对象
        """
        now = time.time_ns()
        monotonic_now = time.perf_counter_ns()
        await self._buffer.put(
            SendingBufferUnit(
                message = message,
                args = args,
                kwargs = kwargs,
                time = now,
                monotonic_time = monotonic_now,
                reply = reply,
                break_code = break_code,
                continue_handler = continue_handler,
            )
        )
    
    async def _send_to_matcher(
        self,
        message: str | Message | MessageSegment,
        reply: bool = True,
        break_code: int = 0,
        continue_handler: bool = False,
        *args,
        **kwargs
    ) -> None:
        """
        发送消息到 Matcher

        :param message: 消息对象
        """
        if self._matcher is not None:
            await self._matcher.send(
                message,
                *args,
                **kwargs
            )
    
    async def _send_to_api(
        self,
        message: str | Message | MessageSegment,
        reply: bool = True,
        break_code: int = 0,
        continue_handler: bool = False,
        *args,
        **kwargs
    ) -> None:
        """
        发送消息到 API

        :param message: 消息对象
        """
        if isinstance(message, MessageSegment):
            message = Message(
                message
            )
        bot = self._persona_info.cached_api
        if self._target_user is not None:
            await bot.send_private_msg(
                user_id = int(self._target_user),
                message = message,
                *args,
                **kwargs
            )
        elif self._target_group is not None:
            await bot.send_group_msg(
                group_id = int(self._target_group),
                message = message,
                *args,
                **kwargs
            )
        elif self._persona_info.source == MessageSource.GROUP and self._persona_info.group_id is not None:
            await bot.send_group_msg(
                group_id = int(self._persona_info.group_id),
                message = message,
                *args,
                **kwargs
            )
        elif self._persona_info.source == MessageSource.PRIVATE:
            await bot.send_private_msg(
                user_id = int(self._persona_info.user_id),
                message = message,
                *args,
                **kwargs
            )
        else:
            raise ValueError("Invalid Message Source")
    
    @staticmethod
    def text_length_score(text: str) -> float:
        """
        计算文本长度得分

        :param text: 文本
        :return: 文本长度得分
        """
        return text_length_score(
            text = text
        )
    
    @property
    def text_length_score_threshold(self) -> float:
        """
        文本长度得分阈值

        :return: 文本长度得分阈值
        """
        if self._persona_info.source == MessageSource.GROUP:
            threshold = storage_configs.text_length_score_configs.threshold.group
        else:
            threshold = storage_configs.text_length_score_configs.threshold.private

        return threshold
    
    async def _send_file(self, url: str, file_name: str) -> None:
        """
        发送文件

        :param url: 文件URL
        :param file_name: 文件名
        """
        try:
            if self._persona_info.source == MessageSource.GROUP and self._persona_info.group_id is not None:
                await send_group_file(
                    bot = self._persona_info.cached_api,
                    group_id = self._persona_info.group_id,
                    url = url,
                    file_name = file_name
                )
            elif self._persona_info.source == MessageSource.PRIVATE:
                await send_private_file(
                    bot = self._persona_info.cached_api,
                    user_id = self._persona_info.user_id,
                    url = url,
                    file_name = file_name
                )
        except ActionFailed as e:
            logger.error(f"Failed to upload file: {e}")
            await self.send_error("Failed to upload file.")
    
    async def send_file(
            self,
            url: str,
            file_name: str,
            break_code: int = 0,
            continue_handler: bool = False
        ) -> None:
        """
        发送文件

        :param url: 文件URL
        :param file_name: 文件名
        """
        await self.file_speed_limiter.submit(
            self._send_file(
                url = url,
                file_name = file_name
            ),
        )
        if continue_handler:
            raise BreakHandler(break_code)
    
    async def _send_poke(
            self,
            group_id: str | None = None,
            user_id: str | None = None,
            break_code: int = 0,
            continue_handler: bool = False
        ) -> None:
        """
        发送戳一戳
        """
        match self._persona_info.source:
            case MessageSource.GROUP:
                if self._persona_info.group_id is not None:
                    await self._persona_info.cached_api.send_poke(
                        group_id = group_id or self._persona_info.group_id,
                        user_id = user_id or self._persona_info.user_id
                    )
            case MessageSource.PRIVATE:
                await self._persona_info.cached_api.send_poke(
                    user_id = user_id or self._persona_info.user_id
                )
            case _:
                await self.send_error("Unsupported message source.")
        if continue_handler:
            raise BreakHandler(break_code)
    
    async def send_poke(
            self,
            group_id: str | None = None,
            user_id: str | None = None
        ) -> None:
        """
        发送戳一戳
        """
        await self.poke_speed_limiter.submit(
            self._send_poke(
                user_id = user_id,
                group_id = group_id
            ),
        )
import asyncio

from nonebot.adapters.onebot.v11 import MessageSegment, Message
from nonebot.internal.matcher.matcher import Matcher
from nonebot.exception import (
    FinishedException,
    StopPropagation
)

from ...assist_func import (
    is_empty_message,
)
from ...text_render.text_render import RendedImage
from ....client_configs import storage_configs
from ...persona_info import PersonaInfo
from ...scene import Scene
from ...namespace import Namespace
from ...text_render.text_render import TextRender
from ...response.response import Response
from ...special_values import NoGive, nogive, is_no_give
from ...chattts import ChatTTSAPI
from typing import (
    Any,
    Type,
    ClassVar,
    NoReturn,
    Literal,
    overload
)
from ..speed_limiter import SpeedLimiter
from ..sending_buffer_unit import SendingBufferUnit
from ....exceptions import (
    BreakHandler,
)
from ....logger import logger as base_logger
from ..send_type import SendType
from ..zone_ugc_right import ZoneUGCRight
from ..typings import (
    SEND_HOOK,
    RENDER_HOOK,
)

logger = base_logger.bind(module = "SendMsg.SendCore")

class BaseSendCore:
    """
    Repeater 统一消息发送核心对象

    Usage:

        >>> 
        ... send_core = SendCore(
        ...     persona_info = PersonaInfo(
        ...         bot = bot,
        ...         event = event,
        ...         args = args
        ...     ),
        ...     matcher = matcher
        ... )
        ...
        >>> # 像 matcher.send() 一样发送消息
        >>> await send_core.send(
        ...     message,
        ...     reply = False, # SendCore 默认会让消息添加 reply 消息段，可用这种方法将其移除
        ...     continue_handler = True
        ... )
        ...
        >>> # 发送一个文件
        >>> await send_core.send_file(
        ...     file_path,
        ...     continue_handler = True
        ... )
        >>> # 发送一个戳一戳
        >>> await send_core.send_poke(
        ...     continue_handler = True
        ... )
        >>> 
        >>> # 复制一个输出为 Buffer 的 SendCore
        >>> # 注意：仅对于消息输出有效
        >>> copied_send_core = send_core.copy(
        ...     send_target = SendTarget.BUFFER,
        ...     continue_handler = True
        ... )
        >>> # 发送一个消息到缓冲区
        >>> await copied_send_core.send(
        ...     "Test", # 此处也可以填写字符串
        ...     continue_handler = True
        ... )
        >>> # 从缓冲区读取内容
        >>> text_buffer: list[str] = []
        >>> while copied_send_core.buffer.qsize() > 0:
        ...     result = await copied_send_core.buffer.get()
        ...     text_buffer.append(result.message)
        >>> # 发送一个消息
        >>> await send_core.send(
        ...     "\n".join(text_buffer),
        ...     continue_handler = True
        ... )
        >>> 
        >>> # 复制并设置目标为 群聊 1234567890
        >>> copied_send_core = send_core.copy(
        ...     continue_handler = True,
        ...     target = Scene(
        ...         source = MessageSource.GROUP,
        ...         id = "1234567890",
        ...     )
        ...     send_target = SendingTarget.API # 只有设置成 API 才能绕过 Matcher 发送消息
        ... )
        >>> # 发送一个消息到群聊 1234567890
        >>> await copied_send_core.send(
        ...     "Test", # 此处也可以填写字符串
        ...     continue_handler = True
        ... )
        >>> 
        >>> # 复制并设置目标为 用户 1234567890
        >>> copied_send_core = send_msg.copy(
        ...     continue_handler = True,
        ...     target = Scene(
        ...         source = MessageSource.PRIVATE,
        ...         id = "1234567890",
        ...     )
        ...     send_target = SendingTarget.API # 也是只有设置成 API 才能绕过 Matcher 发送消息
        ... )
        >>> # 发送一个消息到用户 1234567890
        >>> await copied_send_core.send(
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
    zone_speed_limiter: ClassVar[SpeedLimiter] = SpeedLimiter(
        storage_configs.camouflage.limit_speed_per_minute.zone
    )
    
    @overload
    def __init__(
            self,
            persona_info: PersonaInfo,
            matcher: Type[Matcher],
            reply: MessageSegment | None = None,
            prefix: Message | None = None,
            suffix: Message | None = None,
            target: Scene | None = None,
            send_target: Literal[SendType.MATCHER] = SendType.MATCHER,
            send_hook: list[SEND_HOOK] | None = None,
            render_hook: list[RENDER_HOOK] | None = None,
        ): ...
    
    @overload
    def __init__(
            self,
            persona_info: PersonaInfo,
            matcher: Type[Matcher] | None = None,
            reply: MessageSegment | None = None,
            prefix: Message | None = None,
            suffix: Message | None = None,
            target: Scene | None = None,
            send_target: SendType = SendType.AUTO,
            send_hook: list[SEND_HOOK] | None = None,
            render_hook: list[RENDER_HOOK] | None = None,
        ): ...

    def __init__(
            self,
            persona_info: PersonaInfo,
            matcher: Type[Matcher] | None = None,
            reply: MessageSegment | None = None,
            prefix: Message | None = None,
            suffix: Message | None = None,
            target: Scene | None = None,
            send_target: SendType = SendType.AUTO,
            send_hook: list[SEND_HOOK] | None = None,
            render_hook: list[RENDER_HOOK] | None = None,
        ):
        self._persona_info: PersonaInfo = persona_info
        self._reply: MessageSegment | None = reply
        self._prefix: Message = prefix or Message()
        self._suffix: Message = suffix or Message()
        self._chat_tts_api = ChatTTSAPI()
        self._matcher: Type[Matcher] | None = matcher
        self._target: Scene | None = target
        self._send_hook: list[SEND_HOOK] | None = send_hook
        self._render_hook: list[RENDER_HOOK] | None = render_hook
        
        self._buffer: asyncio.Queue[SendingBufferUnit] = asyncio.Queue()
        self._send_type: SendType = send_target
        match self._send_type:
            case SendType.AUTO:
                if matcher is None:
                    self._send_type = SendType.API
                else:
                    self._send_type = SendType.MATCHER
            case SendType.MATCHER:
                if matcher is None:
                    raise ValueError("Matcher can't be a target, because it's not given.")

    def __repr__(self) -> str:
        args_map:  list[tuple[str, Any]] = [
            ("persona_info", self._persona_info),
            ("matcher", self._matcher),
            ("reply", self._reply),
            ("prefix", self._prefix),
            ("suffix", self._suffix),
            ("target", self._target),
            ("sending_target", self._send_type),
            ("send_hook", self._send_hook),
            ("render_hook", self._render_hook),
        ]
        return f"{self.__class__.__name__}({', '.join([f'{k}={v!r}' for k, v in args_map if v is not None])})"
    
    def copy(
            self,
            persona_info: PersonaInfo | NoGive = nogive,
            matcher: Type[Matcher] | None | NoGive = nogive,
            reply: MessageSegment | None | NoGive = nogive,
            prefix: Message | None | NoGive = nogive,
            suffix: Message | None | NoGive = nogive,
            target: Scene | None | NoGive = nogive,
            send_target: SendType | NoGive = nogive,
            send_hook: list[SEND_HOOK] | None | NoGive = nogive,
            render_hook: list[RENDER_HOOK] | None | NoGive = nogive,
        ) -> "BaseSendCore ":
        persona_info = persona_info if not is_no_give(persona_info) else self._persona_info.copy()
        matcher = matcher if not is_no_give(matcher) else self._matcher
        reply = reply if not is_no_give(reply) else self._reply
        prefix = prefix if not is_no_give(prefix) else self._prefix
        suffix = suffix if not is_no_give(suffix) else self._suffix
        send_target = send_target if not is_no_give(send_target) else self._send_type
        target = target if not is_no_give(target) else self._target
        send_hook = send_hook if not is_no_give(send_hook) else self._send_hook
        render_hook = render_hook if not is_no_give(render_hook) else self._render_hook

        instance = self.__class__(
            persona_info = persona_info,
            matcher = matcher,
            reply = reply,
            prefix = prefix,
            suffix = suffix,
            target = target,
            send_target = send_target,
            send_hook = send_hook,
            render_hook = render_hook
        )
        
        return instance

    @property
    def persona_info(self) -> PersonaInfo:
        return self._persona_info

    @property
    def reply(self) -> MessageSegment | None:
        return self._reply

    @property
    def prefix(self) -> Message:
        return self._prefix

    @property
    def suffix(self) -> Message:
        return self._suffix

    @property
    def chat_tts_api(self) -> ChatTTSAPI:
        return self._chat_tts_api

    @property
    def matcher(self) -> Type[Matcher] | None:
        return self._matcher

    @property
    def target(self) -> Scene | None:
        return self._target

    @property
    def send_hook(self) -> list[SEND_HOOK] | None:
        return self._send_hook

    @property
    def render_hook(self) -> list[RENDER_HOOK] | None:
        return self._render_hook

    @property
    def buffer(self) -> asyncio.Queue[SendingBufferUnit]:
        return self._buffer

    @property
    def send_type(self) -> SendType:
        return self._send_type

    @send_type.setter
    def send_type(self, sending_target: SendType):
        """
        设置当前消息的发送目标
        """
        if not isinstance(sending_target, SendType):
            raise TypeError(f"sending_target must be SendingTarget, not {type(sending_target).__name__}")

        self._send_type = sending_target
        match self._send_type:
            case SendType.AUTO:
                if self._matcher is None:
                    self._send_type = SendType.API
                else:
                    self._send_type = SendType.MATCHER
            case SendType.MATCHER:
                if self._matcher is None:
                    raise ValueError("Matcher can't be a target, because it's not given.")
    @staticmethod
    def handler_finished() -> NoReturn:
        """
        关闭整个处理流程树

        :raise: FinishedException
        """
        raise FinishedException

    @staticmethod
    def block_propagation() -> NoReturn:
        """
        阻止事件向低优先级节点传播

        :raise: StopPropagation
        """
        raise StopPropagation

    @staticmethod
    def break_handler(code: int = 0) -> NoReturn:
        """
        跳出当前处理函数

        :raise: BreakHandler
        """
        raise BreakHandler(code)

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
        quality: int | None = None,
        namespace: Namespace | None = None
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
        :param namespace: 命名空间
        :return: 渲染图片的 URL
        """
        raise NotImplementedError
    
    @overload
    async def send(
            self,
            message: str | Message | MessageSegment,
            reply: bool = True,
            break_code: int = 0,
            continue_handler: Literal[False] = False
        ) -> NoReturn: ...
    
    @overload
    async def send(
            self,
            message: str | Message | MessageSegment,
            reply: bool = True,
            break_code: int = 0,
            continue_handler: Literal[True] = True
        ) -> None: ...
    
    async def send(
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
        if not is_empty_message(message):
            send_msg = self._prefix + message + self._suffix

            if reply:
                if self._reply is not None:
                    send_msg = self._reply + send_msg

            if self._send_hook is not None and self._send_type != SendType.NULL:
                tasks: list[asyncio.Task[bool | None]] = [
                    asyncio.create_task(
                        hook(
                            type = self._send_type,
                            message = send_msg,
                            reply = reply,
                            break_code = break_code,
                            continue_handler = continue_handler
                        )
                    )
                    for hook in self._send_hook
                ]
                task_results = await asyncio.gather(*tasks)
                for result in task_results:
                    if result is False:
                        if not continue_handler:
                            self.break_handler(break_code)
                        return
            try:
                await self.send_to_target(
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

    async def send_to_target(
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
        match self._send_type:
            case SendType.BUFFER:
                logger.info(
                    "Send to buffer: \n{message}",
                    message = message
                )
                await self.send_to_queue(
                    message,
                    reply = reply,
                    break_code = break_code,
                    continue_handler = continue_handler,
                    *args,
                    **kwargs
                )
            case SendType.MATCHER:
                logger.info(
                    "Send to matcher: \n{message}",
                    message = message
                )
                await self.message_speed_limiter.submit(
                    task = self.send_to_matcher(
                        message,
                        reply = reply,
                        break_code = break_code,
                        continue_handler = continue_handler,
                        *args,
                        **kwargs
                    )
                )
            case SendType.API:
                logger.info(
                    "Send to api: \n{message}",
                    message = message
                )
                await self.message_speed_limiter.submit(
                    task = self.send_to_api(
                        message,
                        reply = reply,
                        break_code = break_code,
                        continue_handler = continue_handler,
                        *args,
                        **kwargs
                    )
                )    
            case SendType.NULL:
                logger.info(
                    "Send to null: \n{message}",
                    message = message
                )
                pass

    async def send_to_queue(
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
        raise NotImplementedError

    async def send_to_matcher(
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
        raise NotImplementedError
    
    async def send_to_api(
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
        raise NotImplementedError
    
    async def _send_file(
            self,
            url: str,
            file_name: str
        ) -> str | None:
        """
        发送文件

        :param url: 文件URL
        :param file_name: 文件名
        """
        raise NotImplementedError
    
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
        file_id = await self.file_speed_limiter.submit(
            self._send_file(
                url = url,
                file_name = file_name
            ),
        )
        if self._send_hook is not None:
            tasks: list[asyncio.Task[bool | None]] = [
                asyncio.create_task(
                    hook(
                        type = SendType.API,
                        message = Message(
                            MessageSegment(
                                "file",
                                {
                                    "id": file_id,
                                    "url": url,
                                    "name": file_name,
                                    "file_id": file_id
                                }
                            )
                        ),
                        reply = False,
                        break_code = break_code,
                        continue_handler = continue_handler
                    )
                )
                for hook in self._send_hook
            ]
            task_results = await asyncio.gather(*tasks)
            for result in task_results:
                if result is False:
                    if not continue_handler:
                        self.break_handler(break_code)
                    return
        if not continue_handler:
            self.break_handler(break_code)
    
    async def _send_poke(
            self,
            namespace: Namespace,
        ) -> None:
        """
        发送戳一戳
        """
        raise NotImplementedError
    
    async def send_poke(
            self,
            namespace: Namespace,
            break_code: int = 0,
            continue_handler: bool = False
        ) -> None:
        """
        发送戳一戳
        """
        await self.poke_speed_limiter.submit(
            task = self._send_poke(
                namespace = namespace
            ),
        )
        if not continue_handler:
            self.break_handler(break_code)

    async def _send_zone(
            self,
            content: str,
            images: list[str] | None = None,
            ugc_right: ZoneUGCRight | None = None,
            target_uins: list[int] | None = None,
        ) -> str | None:
        """
        发送 QQ 空间说说

        :param content: 说说内容
        :param images: 图片链接列表
        :param ugc_right: 权限
        :param target_uins: 目标用户列表
        """
        raise NotImplementedError

    async def send_zone(
            self,
            content: str,
            images: list[str] | None = None,
            ugc_right: ZoneUGCRight | None = None,
            target_uins: list[int] | None = None,
            break_code: int = 0,
            continue_handler: bool = False
        ) -> str | None:
        """
        发送 QQ 空间说说

        :param content: 说说内容
        :param images: 图片链接列表
        :param ugc_right: 权限
        :param target_uins: 目标用户列表
        """
        result = await self.zone_speed_limiter.submit(
            self._send_zone(
                content,
                images,
                ugc_right,
                target_uins,
            )
        )

        if not continue_handler:
            self.break_handler(break_code)

        return result
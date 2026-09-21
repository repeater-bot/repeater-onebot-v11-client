from __future__ import annotations

import copy
import uuid
import httpx

from nonebot import get_bots
from nonebot.adapters.onebot.v11 import (
    Bot,
    MessageEvent,
    MessageSegment,
    Message
)
from nonebot.internal.adapter.adapter import Adapter
from typing import (
    Any,
    AsyncGenerator,
    Container,
    Iterable,
    Callable
)

from nonebot.internal.adapter.bot import Bot
from ..assist_func import (
    at_with_name,
    image_to_text,
    get_reply_msgs,
    get_forward_msgs,
    get_message_event,
    generates_text_from_messages_list,
    get_reply_chain
)
from ..namespace import MessageSource, Namespace
from .enter_type import EnterType
from .file_info import FileInfo
from .cached_apis import CachedAPI
from ..user_config import UserConfigLoader, UserConfigs
from ..permission_checker import PermissionChecker
from ...client_configs import storage_configs
from ..special_values import NoGive, nogive
from ._copy_value import copy_value

class PersonaInfo:
    """
    Repeater 统一输入处理对象

    Usage:
    
        >>> from nonebot import on_command
        >>> from nonebot.adapters.onebot.v11 import Bot, MessageEvent, Message, MessageSegment
        >>> from nonebot.params import CommandArg
        >>> 
        >>> @on_command("my_command", aliases={"my_commmand_alias"}, priority=5)
        >>> async def my_command(
        ...     bot: Bot,
        ...     event: MessageEvent,
        ...     args: Message = CommandArg()
        ... ):
        ...     persona_info = PersonaInfo(bot, event, args)
        ...     if persona_info:
        ...         user_id = persona_info.user_id
        ...         group_id = persona_info.group_id
        ...         user_configs = await persona_info.get_user_configs()
        ...
        ...         async for ref in persona_info.from_reference_chain():
        ...             ref_user_id = ref.user_id
        ...             # do something
        ...             pass
        ...     else:
        ...         # empty message
        ...         pass
    """
    def __init__(
            self,
            bot: Bot,
            event: MessageEvent,
            args: str | Message | None = None,
            task_id: uuid.UUID | None = None,
            enter_type: EnterType = EnterType.Command
        ) -> None:
        """
        创建一个 PersonaInfo 对象
        
        :param bot: Bot 对象
        :param event: MessageEvent 对象
        :param args: Message 或 None，默认为 None
        """
        self._bot: Bot = bot
        self._cached_api: CachedAPI = CachedAPI(
            self._bot.adapter,
            self._bot.self_id
        )
        self._message_event: MessageEvent = event
        self._task_id: uuid.UUID = task_id or uuid.uuid4()

        self._args: Message | None
        if isinstance(args, Message):
            self._args = args
        elif isinstance(args, str):
            self._args = Message(args)
        else:
            self._args = None
        
        self._group_id: str | None = None
        self._source = MessageSource(event.message_type.strip().lower())
        self._enter_type: EnterType = enter_type
        self._raw_message_event: MessageEvent | None = None
        self._self_id: str = bot.self_id

        if self._source == MessageSource.GROUP:
            try:
                self._group_id = str(event.model_dump()["group_id"])
                if self._group_id is None:
                    raise ValueError("Is Group, But Group ID is None")
            except KeyError:
                raise ValueError("Is Group, But Group ID is Not Found")
        
        self._super_permissions_checker: PermissionChecker = PermissionChecker(storage_configs.super_permissions)
        self._user_config_loader = UserConfigLoader(self.namespace)

    def __repr__(self) -> str:
        args_map:  list[tuple[str, Any]] = [
            ("bot", self._bot),
            ("event", self._message_event),
            ("args", self._args),
            ("task_id", self._task_id),
            ("enter_type", self._enter_type),
        ]
        return f"{self.__class__.__name__}({', '.join([f'{k}={v!r}' for k, v in args_map if v is not None])})"
    
    @classmethod
    def from_command(cls, bot: Bot, event: MessageEvent, args: Message | None = None, task_id: uuid.UUID | None = None) -> PersonaInfo:
        """
        从命令事件构建

        :param bot: Bot
        :param event: MessageEvent
        :param args: Message | None
        """
        persona_info = cls(
            bot = bot,
            event = event,
            args = args,
            task_id = task_id,
            enter_type = EnterType.Command
        )
        return persona_info
    
    @classmethod
    def from_message(cls, bot: Bot, event: MessageEvent, task_id: uuid.UUID | None = None) -> PersonaInfo:
        """
        从消息事件创建

        :param bot: 机器人实例
        :param event: 消息事件
        """
        persona_info = cls(
            bot = bot,
            event = event,
            task_id = task_id,
            enter_type = EnterType.Message
        )
        return persona_info
    
    @classmethod
    def from_horizontal(cls, persona_info: PersonaInfo) -> PersonaInfo:
        """
        从横向模式进入

        :param persona_info: 来自横向调用的 PersonaInfo
        """
        persona_info = cls(
            bot = persona_info.bot,
            event = persona_info.event,
            args = persona_info.args,
            task_id = persona_info.task_id,
            enter_type = EnterType.Horizontal
        )
        return persona_info
    
    def copy(
            self,
            bot: Bot | NoGive = nogive,
            event: MessageEvent | NoGive = nogive,
            args: Message | None | NoGive = nogive,
            task_id: uuid.UUID | None | NoGive = nogive,
            enter_type: EnterType | NoGive = nogive,
            copydata: bool = False,
            deepcopy: bool = False
        ) -> PersonaInfo:
        """
        复制一个 PersonaInfo 对象

        :param bot: 机器人实例
        :param event: 消息事件
        :param args: 消息
        :param copyargs: 复制 args (如果设置为 `True`，则 `args` 为 `None` 时继承当前 args)
        :param copydata: 复制数据
        :param deepcopy: 是否深拷贝复制数据 (需要 `copydata` 为 `True`)
        """
        new_bot = copy_value(
            value = bot,
            get_new_value_deep = lambda: copy.deepcopy(self.bot),
            get_new_value_copy = lambda: copy.copy(self.bot),
            get_new_value = lambda: self.bot,
            copydata = copydata,
            deepcopy = deepcopy
        )

        new_event = copy_value(
            value = event,
            get_new_value_deep = lambda: self._message_event.model_copy(deep = True),
            get_new_value_copy = lambda: self._message_event.model_copy(),
            get_new_value = lambda: self._message_event,
            copydata = copydata,
            deepcopy = deepcopy
        )

        new_args = copy_value(
            value = args,
            get_new_value_deep = lambda: copy.deepcopy(self._args) if self._args is not None else None,
            get_new_value_copy = lambda: self._args.copy() if self._args is not None else None,
            get_new_value = lambda: self.args,
            copydata = copydata,
            deepcopy = deepcopy
        )

        new_task_id = copy_value(
            value = task_id,
            get_new_value_deep = lambda: copy.deepcopy(self._task_id),
            get_new_value_copy = lambda: copy.copy(self._task_id),
            get_new_value = lambda: self._task_id,
            copydata = copydata,
            deepcopy = deepcopy
        )

        new_enter_type = copy_value(
            value = enter_type,
            get_new_value_deep = lambda: self._enter_type,
            get_new_value_copy = lambda: self._enter_type,
            get_new_value = lambda: self._enter_type,
            copydata = copydata,
            deepcopy = deepcopy
        )
        
        return self.__class__(
            bot = new_bot,
            event = new_event,
            args = new_args,
            task_id = new_task_id,
            enter_type = new_enter_type,
        )
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other, PersonaInfo):
            return (
                self._bot == other._bot and
                self._message_event == other._message_event and
                self._args == other._args
            )
        return False
    
    async def from_message_event(
            self,
            event: MessageEvent | None,
            copydata: bool = False,
            deepcopy: bool = False
        ) -> PersonaInfo:
        """
        从 MessageEvent 构建 PersonaInfo
        """
        if event is None:
            event = await self.get_message_event()
        instance = self.copy(
            copydata = copydata,
            deepcopy = deepcopy
        )
        instance._enter_type = self._enter_type
        return instance

    async def from_reply_reversed_chain(
            self,
            max_depth: int | None = None,
            break_chain: Callable[[PersonaInfo], bool] = lambda _: False,
            postcheck: bool = False,
            copydata: bool = False,
            deepcopy: bool = False
        ) -> list[PersonaInfo]:
        """
        从引用链构建 PersonaInfo 实例，且反向

        注：解析时，它会默认消息段中只有一个 reply 消息段，
        如果有存在多个，则使用第一个

        :param max_depth: 最大迭代深度
        :param break_chain: 断开链的回调函数
        :param postcheck: 将原本在前面的 break 检查移动到后方
        :param copydata: 是否复制数据
        :param deepcopy: 是否深拷贝数据
        """
        reference_chain: list[PersonaInfo] = []
        async for persona_info in self.from_reply_chain(
            max_depth = max_depth,
            copydata = copydata,
            deepcopy = deepcopy
        ):
            if postcheck:
                reference_chain.append(persona_info)
                if break_chain(persona_info):
                    break
            else:
                if break_chain(persona_info):
                    break
                reference_chain.append(persona_info)
        return reference_chain[::-1]
    
    async def from_reply_chain(
            self,
            max_depth: int | None = None,
            copydata: bool = False,
            deepcopy: bool = False
        ) -> AsyncGenerator[PersonaInfo, None]:
        """
        从引用链构建 PersonaInfo 实例

        注：解析时，它会默认消息段中只有一个 reply 消息段，
        如果有存在多个，则使用第一个

        :param copydata: 是否复制数据
        :param deepcopy: 是否深拷贝数据
        """
        async for event in self.get_reply_chain(max_depth):
            instance = self.copy(
                event = event,
                args = None,
                copydata = copydata,
                deepcopy = deepcopy
            )
            yield instance
    
    async def from_reply(self) -> PersonaInfo | None:
        """
        从回复引用构建 PersonaInfo 实例

        注：解析时，它会默认消息段中只有一个 reply 消息段，
        如果有存在多个，则使用第一个
        """
        event = await self.get_message_event()
        reply_id: str | None = None
        for message in event.message:
            if message.type == "reply":
                reply_id = message.data["id"]
                break
        if reply_id is None:
            return None
        reply_event = await self.get_message_event(message_id = int(reply_id))
        persona_info = self.__class__(
            bot = self.bot,
            event = reply_event
        )
        return persona_info
    
    @property
    def enter_type(self) -> EnterType:
        """
        获取进入模式
        """
        return self._enter_type
    
    def __bool__(self) -> bool:
        """
        判断消息是否为空
        """
        for message in self.message:
            if message.type == "text":
                if message.data["text"]:
                    return True
            elif message.type not in ["at", "reply"]:
                return True
        return False

    @property
    def task_id(self) -> uuid.UUID:
        """
        任务 ID
        """
        return self._task_id
    
    @property
    def adapter(self) -> Adapter:
        """
        Bot 的 Adapter 实例
        """
        return self._bot.adapter
    
    @property
    def has_super_permissions(self) -> bool:
        """
        当前发起请求的用户是否具有超级权限
        """
        return self._super_permissions_checker.check(self.namespace)
    
    @property
    def is_self(self) -> bool:
        """
        当前发起请求的用户是否为自身
        """
        return self.user_id == self.self_id
    
    @property
    def self_id(self) -> str:
        """
        机器人自身 ID
        """
        return self._self_id
    
    @property
    def super_permissions(self) -> PermissionChecker:
        """
        超级权限检查器
        """
        return self._super_permissions_checker.copy()
    
    @property
    def message_id(self) -> int:
        """
        当前消息 ID
        """
        return self._message_event.message_id

    @property
    def group_id(self) -> str | None:
        """
        当前群号
        """
        if self._group_id is None:
            return None
        return self._group_id
    
    @property
    def user_id(self) -> str:
        """
        当前用户 ID
        """
        return str(self._message_event.user_id)
    
    @property
    def nickname(self) -> str | None:
        """
        当前用户昵称
        """
        return self._message_event.sender.nickname
    
    @property
    def card(self) -> str | None:
        """
        当前用户名片

        通常情况下，群名片会覆盖昵称
        """
        return self._message_event.sender.card
    
    @property
    def display_name(self) -> str:
        """
        当前用户显示名称

        自动处理用户昵称、群名片
        """
        if self.card:
            return self.card
        else:
            if self.nickname is not None:
                return self.nickname
            return ""
    
    @property
    def age(self) -> int | None:
        """
        当前用户年龄
        """
        return self._message_event.sender.age
    
    @property
    def gender(self) -> str | None:
        """
        当前用户性别
        """
        return self._message_event.sender.sex
    
    @property
    def bot(self) -> Bot | Bot:
        """
        Bot 实例
        """
        return self._bot
    
    @property
    def cached_api(self) -> CachedAPI:
        """
        Bot 实例（带 API 请求缓存）
        """
        return self._cached_api
    
    @property
    def bots(self) -> dict[str, Bot]:
        """
        所有 Bot 实例
        """
        return get_bots()
    
    @property
    def event(self) -> MessageEvent:
        """
        消息事件对象
        """
        return self._message_event

    @property
    def namespace(self) -> Namespace:
        """
        当前用户所在命名空间
        """
        if self._source == MessageSource.GROUP:
            return Namespace(
                mode = MessageSource.GROUP,
                group_id = self._group_id,
                user_id = self.user_id
            )
        else:
            return Namespace(
                mode = MessageSource.PRIVATE,
                user_id = self.user_id
            )
    
    @property
    def namespace_str(self) -> str:
        """
        当前用户所在命名空间字符串
        """
        return self.namespace.namespace_str
    
    @property
    def private_namespace(self) -> Namespace:
        """
        当前用户所在命名空间（私聊）
        """
        return Namespace(
            mode = MessageSource.PRIVATE,
            user_id = self.user_id
        )
    
    @property
    def private_namespace_str(self) -> str:
        """
        当前用户所在命名空间字符串（私聊）
        """
        return self.private_namespace.namespace_str
    
    def this_group_namespace(self, user_id: str) -> Namespace:
        """
        基于当前群组信息，构建指定 user_id 的 Namespace 实例
        """
        if self._source == MessageSource.GROUP:
            return Namespace(
                mode = MessageSource.GROUP,
                group_id = self._group_id,
                user_id = user_id
            )
        else:
            return Namespace(
                mode = MessageSource.PRIVATE,
                user_id = user_id
            )

    def group_namespace(self, group_id: str | None = None) -> Namespace:
        """
        当前用户所在命名空间（群聊）
        """
        if group_id is None and self._group_id is None:
            raise RuntimeError("Not found group_id")
        return Namespace(
            mode = MessageSource.GROUP,
            group_id = group_id or self._group_id,
            user_id = self.user_id
        )
    
    def group_namespace_str(self, group_id: str | None = None) -> str:
        """
        当前用户所在命名空间字符串（群聊）
        """
        return self.group_namespace(group_id).namespace_str
    
    @property
    def public_namespace_str(self) -> str:
        """
        当前用户所在命名空间字符串（公共空间）
        """
        return self.namespace.public_space_id
    
    async def get_user_configs(self) -> UserConfigs:
        """
        获取用户配置
        """
        return await self._user_config_loader.load()
    
    async def set_user_configs(self, configs: UserConfigs):
        """
        设置用户配置
        """
        await self._user_config_loader.save(configs)
    
    @property
    def event_message(self) -> Message:
        """
        来自事件的消息
        """
        return self._message_event.message
    
    @property
    def message(self) -> Message:
        """
        消息内容

        如果存在 args 就使用 args，否则使用 event_message
        """
        if self._args is not None:
            return self._args.copy()
        else:
            return self._message_event.message.copy()
    
    @property
    def args(self) -> Message:
        """
        命令参数
        """
        if self._args is not None:
            return self._args.copy()
        else:
            return Message()
    
    @property
    def event_message_str(self) -> str:
        """
        消息事件字符串
        """
        return self.event_message.extract_plain_text()
    
    @property
    def message_str(self) -> str:
        """
        消息字符串
        """
        return self.message.extract_plain_text()
    
    @property
    def message_stripped_str(self) -> str:
        """
        消息字符串（去除首尾空格）
        """
        return self.message_str.strip()
    
    @property
    def event_message_striped_str(self) -> str:
        """
        消息事件字符串（去除首尾空格）
        """
        return self.event_message_str.strip()
    
    @property
    def args_str(self) -> str:
        """
        命令参数字符串
        """
        return self.args.extract_plain_text()

    @property
    def message_cqcode(self) -> str:
        """
        消息字符串 (CQ码)
        """
        return str(self.message)

    @property
    def event_message_cqcode(self) -> str:
        """
        消息事件字符串 (CQ码)
        """
        return str(self.event_message)

    @property
    def args_cqcode(self) -> str:
        """
        命令参数字符串 (CQ码)
        """
        return str(self.args)
    
    @property
    def reply(self) -> MessageSegment:
        """
        引用当前消息的消息段
        """
        return MessageSegment.reply(self.message_id)
    
    @property
    def source(self) -> MessageSource:
        """
        消息来源
        """
        return self._source
    
    @property
    def noself_at_list(self) -> list[str]:
        """
        消息中提及的 user_id 列表（不包括自己）
        """
        at_list: list[str] = []
        if self._message_event is None:
            return at_list
        for segment in self._message_event.message:
            if segment.type == "at":
                mentioned_id = segment.data["qq"]
                # 检查是否@的是非机器人用户
                if mentioned_id != self._bot.self_id:
                    at_list.append(mentioned_id)
        return at_list
    
    @property
    def at_list(self) -> list[str]:
        """
        消息中提及的 user_id 列表
        """
        at_list: list[str] = []
        if self._message_event is None:
            return at_list
        for segment in self._message_event.message:
            if segment.type == "at":
                at_list.append(segment.data["qq"])
        return at_list
    
    async def handle_at_with_name(self) -> Message:
        """
        处理@消息，将@的 user_id 替换为昵称
        """
        return await at_with_name(self._cached_api, self._message_event)
    
    async def image_to_text(self, format: str = "{text}", cite: bool = True, excluded_tags:Container[str] = {}) -> Message:
        """
        将消息内的图片消息段通过 OCR 转换为文字
        """
        return await image_to_text(
            self._cached_api,
            self.message,
            format = format,
            cite = cite,
            excluded_tags = excluded_tags
        )
    
    @property
    def plaintext_message(self) -> str:
        """
        消息的纯文本内容
        """
        return self.message.extract_plain_text()
    
    def get_images_url(self) -> list[str]:
        """
        获取消息内的图片消息段

        :param base64: 是否返回 base64 编码的图片
        :return: 图片的 URL 列表
        """
        urls: list[str] = []
        for msg in self.message:
            if msg.type == "image":
                urls.append(msg.data["url"])
        return urls
    
    def get_video_url(self) -> list[str]:
        """
        获取消息内的视频消息段

        :return: 视频的 URL 列表
        """
        urls: list[str] = []
        for msg in self.message:
            if msg.type == "video":
                urls.append(msg.data["url"])
        return urls
    
    def get_audio_url(self) -> list[str]:
        """
        获取消息内的音频消息段

        :return: 音频的 URL 列表
        """
        urls: list[str] = []
        for msg in self.message:
            if msg.type == "record":
                urls.append(msg.data["url"])
        return urls
    
    def get_file_infos(self) -> list[FileInfo]:
        """
        获取消息内的文件消息段

        :return: 文件的 URL 列表
        """
        urls: list[FileInfo] = []
        for msg in self.message:
            if msg.type == "file":
                urls.append(
                    FileInfo(**msg.data)
                )
        return urls
    
    async def get_reply_chain(self, max_depth: int | None = None) -> AsyncGenerator[MessageEvent, None]:
        """
        获取回复链

        注：解析时，它会默认消息段中只有一个 reply 消息段，
        如果有存在多个，则使用第一个
        """

        if max_depth is None:
            max_depth = storage_configs.max_reply_chain_length

        # 经过框架处理的 Event 中可能并未包含 reply 消息段
        # 需要重新获取原始 Event
        if "reply" in self.message:
            message = self.message
        else:
            event = await self.get_message_event()
            message = event.message

        chain = get_reply_chain(
            bot = self._cached_api,
            message = message,
            max_depth = max_depth
        )
        async for msg in chain:
            yield msg
    
    async def get_reply_msgs(self, message: Message | None = None) -> list[MessageEvent]:
        """
        获取回复消息

        :param message: 消息
        :return: 回复消息
        """
        return await get_reply_msgs(
            self._cached_api,
            message if message is not None else self.message
        )
    
    async def get_forward_msgs(self) -> list[MessageEvent]:
        """
        获取转发消息

        :return: 转发消息
        """
        return await get_forward_msgs(
            self._cached_api,
            self.message
        )
    
    @staticmethod
    def generates_text_from_messages_list(messages: Iterable[dict | MessageEvent]) -> str:
        """
        从消息列表生成文本

        :param messages: 消息列表
        :return: 文本
        """
        return generates_text_from_messages_list(messages)
    
    async def get_message_event(self, message_id: int | None = None) -> MessageEvent:
        """
        获取消息事件 (并非框架报告给 Repeater 的消息事件)

        :param message_id: 消息id
        :return: 消息事件
        """
        return await get_message_event(
            bot = self._cached_api,
            message_id = message_id if message_id is not None else self.message_id
        )

    def make_message(self, message: str | Iterable[MessageSegment] | MessageSegment | None = None) -> Message:
        """
        生成消息

        :param message: 消息内容
        :return: 消息
        """
        return Message(message)
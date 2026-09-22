import uuid
import httpx
import textwrap

from abc import (
    ABC,
    abstractmethod
)
from ..assist import (
    PersonaInfo,
    SendMsg,
    SendingTarget,
    MessageSource,
    is_iterable,
)
from ..cmd_info import CmdTypes
from .listen_type import ListenType
from ..exceptions import *
from datetime import (
    datetime,
    timedelta
)
from nonebot.adapters.onebot.v11 import (
    Bot,
    Message,
    MessageEvent
)
from nonebot.matcher import Matcher
from nonebot.typing import (
    T_RuleChecker,
    T_PermissionChecker,
    T_State,
    T_Handler
)
from nonebot.rule import (
    Rule,
    to_me
)
from nonebot.permission import Permission
from nonebot.dependencies import Dependent
from nonebot.exception import (
    NoneBotException,
    ActionFailed
)
from ..client_configs import storage_configs
from nonebot import logger
from typing import (
    Any,
    Iterable,
    Collection,
    NoReturn,
    Type,
    TypeVar,
    Generic
)
from .sub_cmd_exit import (
    SubCmdBreaked,
    SubCmdCacelled,
    SubCmdTimeout
)
from .typings import (
    New
)

T = TypeVar("T")

class CommandPackage(ABC, Generic[T]):
    """
    Command Package Base Class
    """

    __time_for_created__: int
    """Time for created"""

    __time_for_created_monotonic__: int
    """Time for created (monotonic)"""

    __time_for_registered__: int
    """Time for registered"""

    __time_for_registered_monotonic__: int
    """Time for registered (monotonic)"""

    __raw_new__: New
    """raw `__new__` method"""

    cmd: str | tuple[str, ...]
    """[Command Only] Command"""

    listen_type: ListenType = ListenType.Command
    """Listen Type (Command or Message)"""

    rule: T_RuleChecker | Rule | None = to_me()
    """Matcher Rule"""
    
    aliases: Iterable[str | tuple[str, ...]] | None = None
    """[Command Only] Command Aliases"""

    force_whitespace: str | bool | None = None
    """[Command Only] Must be followed by a specified space character."""

    permission: T_PermissionChecker | Permission | None = None
    """The permission of the event."""

    handlers: list[T_Handler | Dependent[Any]] | None = None
    """Event handlers list"""

    temp: bool = False
    """Is executed only once."""

    expire_time: datetime | timedelta | None = None
    """Cache expiration time"""

    priority: int = 1
    """Handler priority (the lower the number, the higher the priority) """

    block: bool = True
    """Whether to prevent a message from continuing to spread down after it has been hit."""

    state: T_State | None = None
    """Default state"""

    cmd_type: CmdTypes = CmdTypes.RESERVED
    """Command Type"""

    acceptable_sources: Collection[MessageSource] | None = None
    """This handler's acceptable sources"""

    enabled: bool = True
    """Whether the handler."""

    description: str | Iterable[str] | None = None
    """This handler's description"""

    docs_delimiter: str = "\n"
    """Documentation delimiter"""

    super_permissions: bool = False
    """Whether the Handler need super permissions."""

    send_msg: bool = True
    """Allow sending messages"""

    @property
    def component(self) -> str:
        """The human-readable name of the Handler (required) """
        return f"Repeater.{self.cmd_type.value}.{self.__class__.__name__}"

    @classmethod
    def documents(cls) -> str | Iterable[str] | None:
        """This handler's documentation"""
        pass

    def instance_docs(self) -> str | Iterable[str] | None:
        """This handler's instance documentation"""
        pass
    
    def get_description(self) -> str:
        """Handler description"""
        
        doc = self.description
        if doc is None:
            doc = self.documents()
        if doc is None:
            doc = self.instance_docs()
        if doc is None:
            doc = self.__doc__
        if doc is None:
            doc = ""
        
        if isinstance(doc, str):
            return doc
        elif is_iterable(doc):
            merged_doc = self.docs_delimiter.join(doc)
            return merged_doc
        else:
            logger.warning(
                "Handler {component} has an invalid documentation type: {doc_type}",
                component=self.component,
                doc_type=type(doc).__name__,
            )
            return ""
    
    def __init__(self):
        """
        Initialize the command package.
        """
        pass

    def __pre_init__(self):
        """
        This method will be called before initialization.
        """
        if isinstance(self.description, str):
            self.description = textwrap.dedent(
                self.description.expandtabs(4)
            )

    def __post_init__(self):
        """
        This method will be called after registration is complete.
        """
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}()"

    async def message_enter(self, bot: Bot, event: MessageEvent, matcher: Type[Matcher], task_id: uuid.UUID) -> tuple[PersonaInfo, SendMsg]:
        """
        When you register a Message Handler, the Repeater will call this section before starting to get the abstraction layer object.
        
        You can intercept and do whatever you want here.

        :param bot: Bot object
        :param event: MessageEvent object
        :param matcher: Matcher object
        :return: PersonaInfo object, SendMsg object
        """
        persona_info = PersonaInfo.from_message(
            bot = bot,
            event = event,
            task_id = task_id
        )
        send_msg = SendMsg(
            component = self.component,
            persona_info = persona_info,
            matcher = matcher
        )
        return persona_info, send_msg

    async def command_enter(self, bot: Bot, event: MessageEvent, args: Message, matcher: Type[Matcher], task_id: uuid.UUID) -> tuple[PersonaInfo, SendMsg]:
        """
        When you register a Command Handler, the Repeater will call this section before starting to get the abstraction layer object.
        
        You can intercept and do whatever you want here.

        :param bot: Bot object
        :param event: MessageEvent object
        :param args: Message object
        :param matcher: Matcher object
        :return: PersonaInfo object, SendMsg object
        """
        persona_info = PersonaInfo.from_command(
            bot = bot,
            event = event,
            args = args,
            task_id = task_id
        )
        send_msg = SendMsg(
            component = self.component,
            persona_info = persona_info,
            matcher = matcher
        )
        return persona_info, send_msg

    async def external_enter(self, bot: Bot, event: MessageEvent, args: Message, task_id: uuid.UUID) -> tuple[PersonaInfo, SendMsg]:
        """
        When you register an External Handler, the Repeater will call this section before starting to get the abstraction layer object.
        
        You can intercept and do whatever you want here.

        :param bot: Bot object
        :param event: MessageEvent object
        :param args: Message object
        :param matcher: Matcher object
        :param task_id: Task ID
        :return: PersonaInfo object, SendMsg object
        """
        persona_info = PersonaInfo.from_external(
            bot = bot,
            event = event,
            args = args,
            task_id = task_id
        )
        send_msg = SendMsg(
            component = self.component,
            persona_info = persona_info,
            matcher = None
        )
        return persona_info, send_msg

    
    async def horizontal_enter(self, persona_info: PersonaInfo, send_msg: SendMsg | None = None, task_id: uuid.UUID | None = None) -> tuple[PersonaInfo, SendMsg]:
        """
        This method is called when the call comes from another Handler other than the framework.

        :param persona_info: PersonaInfo object
        :param send_msg: SendMsg object
        :return: PersonaInfo object, SendMsg object
        """
        if send_msg is None:
            send_msg = SendMsg(
                component = self.component,
                persona_info = persona_info,
            )
        persona_info_copy = PersonaInfo.from_horizontal(persona_info, task_id = task_id)
        return persona_info_copy, send_msg

    async def enter_check(self, persona_info: PersonaInfo, send_msg: SendMsg) -> bool:
        """
        This method is called to check if the call is valid.

        :param persona_info: PersonaInfo object
        :param send_msg: SendMsg object
        :return: bool
        """
        block = storage_configs.ignore_enter.ignore_enter_check(persona_info.group_id, persona_info.user_id)

        if block:
            return self.component in storage_configs.ignore_enter.unignore_enter_commands
        return True
    
    async def permissions_check(self, persona_info: PersonaInfo, send_msg: SendMsg) -> bool:
        """
        This method is called to check permissions.

        :param persona_info: PersonaInfo object
        :param send_msg: SendMsg object
        :return: True or False
        """
        behavioral_act = storage_configs.get_behavioral_act(persona_info.user_id)
        if not behavioral_act.check_cmd_types_allowed(self.cmd_type):
            return False
        
        if behavioral_act.block_handlers:
            return False
        
        if behavioral_act.block_output:
            send_msg.sending_target = SendingTarget.NULL
        
        return True
    
    async def enter_handler(self, persona_info: PersonaInfo, send_msg: SendMsg) -> T | NoReturn:
        """
        This method is called before the handler method.

        :param persona_info: PersonaInfo object
        :param send_msg: SendMsg object
        :return: PersonaInfo object, SendMsg object
        """
        result = await self.handler(persona_info, send_msg)
        return result

    @abstractmethod
    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg) -> T | NoReturn:
        """
        Override this method to begin writing your business logic.

        :param persona_info: PersonaInfo object
        :param send_msg: SendMsg object
        """
        pass

    async def on_debug_mode(self, persona_info: PersonaInfo, send_msg: SendMsg) -> T | Any | None | NoReturn:
        """
        This method is executed when the Repeater discovers that the current environment configuration is Debug Mode.

        :param persona_info: PersonaInfo object
        :param send_msg: SendMsg object
        """
        await send_msg.send_debug_mode()
    
    async def on_unacceptable_source(self, persona_info: PersonaInfo, send_msg: SendMsg) -> T | Any | None | NoReturn:
        """
        This method is executed when the Repeater discovers that the current environment configuration is not acceptable.

        :param persona_info: PersonaInfo object
        :param send_msg: SendMsg object
        """
        if self.acceptable_sources is None:
            assert False, "acceptable_sources must be set"
        
        for source in self.acceptable_sources:
            match source:
                case MessageSource.GROUP:
                    match persona_info.source:
                        case MessageSource.PRIVATE:
                            await send_msg.send_error("This command is only available in group chat.")
                        case MessageSource.GROUP:
                            pass
                case MessageSource.PRIVATE:
                    match persona_info.source:
                        case MessageSource.PRIVATE:
                            pass
                        case MessageSource.GROUP:
                            await send_msg.send_error("This command is only available in private chat.")
                case _:
                    pass

    
    async def on_nonebot_exception(self, exception: NoneBotException, persona_info: PersonaInfo, send_msg: SendMsg) -> T | Any | None | NoReturn:
        """
        This method is called when the program throws a NoneBot exception
        You can do some handling here
        Re-throwing is recommended to avoid the framework not receiving the message

        :param exception: NoneBotException object
        :param persona_info: PersonaInfo object
        :param send_msg: SendMsg object
        """
        if isinstance(exception, ActionFailed):
            await send_msg.send_error_render(exception)
        else:
            raise

    async def on_repeater_exception(self, exception: RepeaterException, persona_info: PersonaInfo, send_msg: SendMsg) -> T | Any | None | NoReturn:
        """
        This method is called when the program throws a Repeater exception

        :param exception: RepeaterException object
        :param persona_info: PersonaInfo object
        :param send_msg: SendMsg object
        """
        if isinstance(exception, BreakHandler):
            if isinstance(exception, BreakWithErrorMessage):
                await send_msg.send_error_render(str(exception), continue_handler = True)
            return SubCmdBreaked(exception.code)

    async def on_error(self, exception: Exception, persona_info: PersonaInfo, send_msg: SendMsg) -> T | Any | None | NoReturn:
        """
        The error Handler for the Handler

        It catches all exceptions by default

        Includes all the necessary parts for the framework to work

        So you need to determine them and re-throw them to make sure the framework is working properly

        :param exception: The exception
        :param persona_info: The persona_info object
        :param send_msg: The send_msg object
        """
        if isinstance(exception, httpx.HTTPStatusError):
            await send_msg.send_http_status(
                http_status = exception.response.status_code,
                message = exception.response.text
            )
        else:
            logger.exception(f"Error: {exception}")
            await send_msg.send_error_render(exception)
    
    async def on_interpreter_error(self, exception: BaseException, persona_info: PersonaInfo, send_msg: SendMsg) -> T | Any | None | NoReturn:
        """
        This section is executed when the interpreter encounters an error that is a BaseException but not an Exception.

        You can override this method and do what you need to do.
        It is recommended to keep throwing up at this point. These exceptions probably shouldn't stop there.

        :param exception: The exception
        :param persona_info: The persona_info object
        :param send_msg: The send_msg object
        """
        logger.exception(f"Error: {exception}")
        raise
    
    async def on_cancel(self, persona_info: PersonaInfo, send_msg: SendMsg) -> T | Any | None | NoReturn:
        """
        This section is executed when the Handler is cancelled.

        You can override this method and do what you need to do.

        :param persona_info: The persona_info object
        :param send_msg: The send_msg object
        """
        logger.warning(f"{self.component} cancelled")
        return SubCmdCacelled

    async def on_timeout(self, persona_info: PersonaInfo, send_msg: SendMsg) -> T | Any | None | NoReturn:
        """
        This section is executed when the Handler times out.

        You can override this method and do what you need to do.

        :param persona_info: The persona_info object
        :param send_msg: The send_msg object
        """
        logger.warning(f"{self.component} timed out")
        return SubCmdTimeout(3)
    
    async def handler_exit(self, persona_info: PersonaInfo, send_msg: SendMsg) -> T | Any | None | NoReturn:
        """
        This section is executed whenever the Handler fails or exits.

        You can override this method and do what you need to do.

        :param persona_info: The persona_info object
        :param send_msg: The send_msg object
        :return: None
        """
        logger.info(f"{self.component} exited")

    async def insufficient_access(self, persona_info: PersonaInfo, send_msg: SendMsg) -> T | Any | None | NoReturn:
        """
        If the current user does not meet the permission requirements of the command, execute the method.
        
        :param persona_info: User information
        :param send_msg: Send message interface
        :return: None
        """
        await send_msg.send_error_render("Insufficient access rights.")
        send_msg.break_handler()
    
    async def on_blacklist(self, persona_info: PersonaInfo, send_msg: SendMsg) -> T | Any | None | NoReturn:
        """
        If the current user is in the blacklist, execute the method.

        :param persona_info: User information
        :param send_msg: Send message interface
        :return: None
        """
        logger.warning(
            "User {user_id} is in the blacklist.",
            user_id = persona_info.user_id
        )
        send_msg.break_handler()
    
    @classmethod
    def on_before_instantiate(cls):
        """
        You may want to do something before you instantiate it, and overriding this method can help you.

        :return: None
        """
        pass
    
    def on_registed(self):
        """
        You may want to do something when you complete the registration process,
        overriding this method allows you to perform the task at the end of the registration.

        :return: None
        """
        pass

    def on_matcher_registered(self, matcher: Type[Matcher]) -> Type[Matcher]:
        """
        You may want to do something when you complete the registration process of the matcher,
        overriding this method allows you to perform the task at the end of the registration.

        :param matcher: The matcher that has been registered.
        :return: None
        """
        return matcher

    @classmethod
    def on_reg_failed(cls, exc_type, exc_val, exc_tb):
        """
        If an error occurs during the registration of the current Handler,
        by default, the behavior of the modified method is to throw the original exception.

        :param exc_type: Exception type
        :param exc_val: Exception value
        :param exc_tb: Exception traceback
        :return: None
        """
        raise
    
    @classmethod
    def on_destroy(cls):
        """
        This method is executed when the current Handler is destroyed.
        Both instance and class methods are allowed.
        """
        pass
    
    @classmethod
    async def on_adestroy(cls):
        """
        The asynchronous method executes when the current Handler is destroyed.
        Both instance and class methods are allowed.
        """
        pass
    
    @classmethod
    def on_duplicate_trigger(cls, trigger: str | tuple[str, ...]):
        """
        This section is executed when the Handler is triggered by a duplicate trigger.

        You can override this method and do what you need to do.

        :param persona_info: The persona_info object
        :param send_msg: The send_msg object
        """
        if storage_configs.loading.throw_on_duplicate.trigger:
            raise ValueError(f"Trigger {repr(trigger)} is already registered")
        else:
            logger.warning(
                "Trigger {trigger} is already registered, this can have undesired consequences.",
                trigger = repr(trigger)
            )

    @classmethod
    def on_duplicate_type(cls):
        """
        This section is executed when the type is triggered by a duplicate type.

        You can override this method and do what you need to do.

        :param persona_info: The persona_info object
        :param send_msg: The send_msg object
        """
        if storage_configs.loading.throw_on_duplicate.type:
            raise ValueError(f"Handler Type {repr(cls)} is already registered")
        else:
            logger.warning(
                "Handler type {handler} is already registered, this may result in overwriting.",
                handler = repr(cls)
            )

    @classmethod
    def on_duplicate_class_name(cls, other: "CommandPackage[Any]"):
        """
        This section is executed when the class name is triggered by a duplicate class name.

        You can override this method and do what you need to do.

        :param persona_info: The persona_info object
        :param send_msg: The send_msg object
        """
        if storage_configs.loading.throw_on_duplicate.class_name:
            raise ValueError(f"Handler class name {cls.__name__} and {other.component} is already registered")
        else:
            logger.warning(
                "Handler class name {class_name} is already registered, this may result in overwriting.",
                class_name = cls.__name__
            )

    def on_duplicate_component(self, other: "CommandPackage[Any]"):
        """
        This section is executed when the component is triggered by a duplicate component.

        You can override this method and do what you need to do.

        :param persona_info: The persona_info object
        :param send_msg: The send_msg object
        """
        if storage_configs.loading.throw_on_duplicate.handler:
            raise ValueError(f"Component {self.component} and {other.component} is already registered")
        else:
            logger.warning(
                "Component {component} and {other_component} is already registered, this may result in overwriting.",
                component = self.component,
                other_component = other.component
            )

    def on_duplicate_handler(self):
        """
        This section is executed when the Handler is triggered by a duplicate handler.

        You can override this method and do what you need to do.

        :param persona_info: The persona_info object
        :param send_msg: The send_msg object
        """
        if storage_configs.loading.throw_on_duplicate.handler:
            raise ValueError(f"Handler {self.component} is already registered")
        else:
            logger.warning(
                "Handler {handler} and {other_handler} is already registered, this may result in overwriting.",
                handler = self.component
            )

    @classmethod
    def on_duplicate_matcher(cls, matcher: Type[Matcher]):
        """
        This section is executed when the matcher is triggered by a duplicate matcher.

        You can override this method and do what you need to do.

        :param persona_info: The persona_info object
        :param send_msg: The send_msg object
        """
        if storage_configs.loading.throw_on_duplicate.matcher:
            raise ValueError(f"The {repr(cls)} Matcher {repr(matcher)} is re-registered.")
        else:
            logger.warning(
                "The {handler} matcher {matcher} is already registered, this may result in overwriting.",
                handler = repr(cls),
                matcher = repr(matcher)
            )

    async def on_framework_startup(self):
        """
        This section is executed when the framework is started.

        You can override this method and do what you need to do.
        """
        pass

    async def on_framework_shutdown(self):
        """
        This section is executed when the framework is shutdown.

        You can override this method and do what you need to do.
        """
        pass

    async def on_bot_connect(self, bot: Bot):
        """
        This section is executed when the bot is connected.

        You can override this method and do what you need to do.

        :param bot: The bot object
        """
        pass

    async def on_bot_disconnect(self, bot: Bot):
        """
        This section is executed when the bot is disconnected.

        You can override this method and do what you need to do.

        :param bot: The bot object
        """
        pass
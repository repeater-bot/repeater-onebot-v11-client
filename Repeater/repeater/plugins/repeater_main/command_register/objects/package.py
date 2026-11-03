import uuid
import httpx
import textwrap

from abc import (
    ABC,
    abstractmethod
)
from ...assist import (
    PersonaInfo,
    EnterType,
    SendMsg,
    SendingTarget,
    MessageSource,
    is_iterable,
)
from ...cmd_info import CmdTypes
from .listen_type import ListenType
from ...exceptions import *
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
from ...client_configs import storage_configs
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
    SubCmdCancelled,
    SubCmdTimeout
)
from ..typings import (
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

    __raw_new__: New | None = None
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

    priority: int = 10
    """Handler priority (the lower the number, the higher the priority) """

    block: bool = True
    """Whether to prevent a message from continuing to spread down after it has been hit."""

    state: T_State | None = None
    """Default state"""

    cmd_type: str | CmdTypes = CmdTypes.RESERVED
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
        if isinstance(self.cmd_type, CmdTypes):
            return f"Repeater.{self.cmd_type.value}.{self.__class__.__name__}"
        else:
            return f"Repeater.{self.cmd_type}.{self.__class__.__name__}"

    @classmethod
    def package_path(cls) -> str:
        """The path of the Handler (required) """
        return f"{cls.__module__}.{cls.__qualname__}"

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

    async def message_enter(self, task_id: uuid.UUID, bot: Bot, event: MessageEvent, matcher: Type[Matcher]) -> tuple[PersonaInfo, SendMsg]:
        """
        Called by the message-matcher wrapper (CommandCaller.get_message_handler) before a run
        starts, for every message this package matches.

        The default implementation builds PersonaInfo.from_message plus a SendMsg bound to this
        package and the matcher. The pair returned here is what the run executes with, so
        overriding it changes both the abstraction layer and where replies are sent.

        :param task_id: Task ID
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
            matcher = matcher,
            reply = persona_info.reply
        )
        return persona_info, send_msg

    async def command_enter(self, task_id: uuid.UUID, bot: Bot, event: MessageEvent, args: Message, matcher: Type[Matcher]) -> tuple[PersonaInfo, SendMsg]:
        """
        Called by the command-matcher wrapper (CommandCaller.get_command_handler) before a run
        starts, for every message that matches this package's command.

        The default implementation builds PersonaInfo.from_command (enter type Command) plus a
        SendMsg bound to this package and the matcher. The returned pair is what the run executes
        with, so overriding it changes both the abstraction layer and where replies are sent.

        :param task_id: Task ID
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
            matcher = matcher,
            reply = persona_info.reply
        )
        return persona_info, send_msg

    async def external_enter(self, task_id: uuid.UUID, bot: Bot, event: MessageEvent, args: Message | None, output: bool = True) -> tuple[PersonaInfo, SendMsg]:
        """
        Called by CommandCaller.external_enter for the External Trigger HTTP entry, before a run
        starts; this package has no matcher on that path.

        The default implementation builds PersonaInfo.from_external plus a SendMsg whose matcher
        is None; when output is False the sending target is set to BUFFER, so messages are queued
        instead of sent. The returned pair is what the run executes with.

        :param task_id: Task ID
        :param bot: Bot object
        :param event: MessageEvent object
        :param args: Message object
        :param output: Whether to send the result; False routes messages to the buffer instead
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
        if not output:
            send_msg.sending_target = SendingTarget.BUFFER
        return persona_info, send_msg

    
    async def horizontal_enter(self, persona_info: PersonaInfo, send_msg: SendMsg | None = None, task_id: uuid.UUID | None = None) -> tuple[PersonaInfo, SendMsg]:
        """
        Called by CommandCaller.horizontal_call and horizontal_enter_wait_created before a
        horizontal call; the pair returned here is what the sub-call runs with.

        The default implementation returns a copy of persona_info with enter_type Horizontal and
        the new task id, creating a SendMsg only when send_msg is None - a passed one is returned
        unchanged.

        :param persona_info: PersonaInfo object of the calling Handler
        :param send_msg: SendMsg object of the calling Handler, None means "create one"
        :param task_id: Task ID assigned to the horizontal call
        :return: PersonaInfo object, SendMsg object that the sub-call will run with
        """
        persona_info_copy = PersonaInfo.from_horizontal(persona_info, task_id = task_id)
        if send_msg is None:
            send_msg = SendMsg(
                component = self.component,
                persona_info = persona_info_copy,
                reply = persona_info_copy.reply
            )
        return persona_info_copy, send_msg

    async def enter_check(self, persona_info: PersonaInfo, send_msg: SendMsg) -> bool:
        """
        Called by CommandCaller._enter_handler as the first enter gate, before permissions_check;
        the Handler body is never reached when this returns False.
        The caller then logs "Enter check blocked" and breaks the run with send_msg.break_handler(1);
        calling break_handler(code) inside this method instead rejects the call silently. The
        default implementation returns False only when the group/user is on the ignore-enter list
        and this component is not in unignore_enter_commands.

        :param persona_info: PersonaInfo object
        :param send_msg: SendMsg object
        :return: bool - False rejects the call
        """
        block = storage_configs.ignore_enter.ignore_enter_check(persona_info.group_id, persona_info.user_id)

        if block:
            return self.component in storage_configs.ignore_enter.unignore_enter_commands
        return True
    
    async def permissions_check(self, persona_info: PersonaInfo, send_msg: SendMsg) -> bool:
        """
        Called by CommandCaller._enter_handler right after enter_check and before the
        acceptable-source check; the Handler body is never reached when this returns False.
        The caller then returns insufficient_access(...), whose default implementation posts
        "Insufficient access rights." and breaks the run with code 1. The default implementation
        here returns False when the cmd_type is not allowed, block_handlers is set, or
        super_permissions is missing; block_output only sets the sending target to NULL.

        :param persona_info: PersonaInfo object
        :param send_msg: SendMsg object
        :return: bool - False rejects the call
        """
        behavioral_act = storage_configs.get_behavioral_act(persona_info.user_id)
        
        if behavioral_act.block_output:
            send_msg.sending_target = SendingTarget.NULL
        
        if not behavioral_act.check_cmd_types_allowed(self.cmd_type):
            return False
        
        if behavioral_act.block_handlers:
            return False

        if self.super_permissions and not persona_info.has_super_permissions:
            return False
        
        return True
    
    async def enter_handler(self, persona_info: PersonaInfo, send_msg: SendMsg) -> T | NoReturn:
        """
        Called by CommandCaller._enter_handler once the enter gates pass, as a task wrapped in
        asyncio.wait_for(..., timeout=storage_configs.handler_timeout).
        The default implementation awaits self.handler(persona_info, send_msg) and returns its
        result, so overriding this method replaces the call to the Handler body.

        :param persona_info: PersonaInfo object
        :param send_msg: SendMsg object
        :return: the value returned by handler
        """
        result = await self.handler(persona_info, send_msg)
        return result

    @abstractmethod
    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg) -> T | NoReturn:
        """
        Called by enter_handler by default; implement it as the Handler body.
        The value returned here becomes the result of the run: a SubCmdExit subclass is
        instantiated and its code used as the return code, any other value counting as 0.
        Raising BreakHandler ends the run through on_repeater_exception, other Exception instances
        go to on_error and NoneBotException to on_nonebot_exception.

        :param persona_info: PersonaInfo object
        :param send_msg: SendMsg object
        """
        pass

    async def on_debug_mode(self, persona_info: PersonaInfo, send_msg: SendMsg) -> T | Any | None | NoReturn:
        """
        Called by CommandCaller._enter_handler instead of enter_handler when the run is in debug
        mode; the Handler body is not called on this path.
        The default implementation awaits send_msg.send_debug_mode(), which echoes the parsed
        command back to the chat and raises BreakHandler(0), so the run ends as SubCmdBreaked(0).

        :param persona_info: PersonaInfo object
        :param send_msg: SendMsg object
        """
        await send_msg.send_debug_mode()
    
    async def on_unacceptable_source(self, persona_info: PersonaInfo, send_msg: SendMsg) -> T | Any | None | NoReturn:
        """
        Called by CommandCaller._enter_handler when check_acceptable_sources rejects the call,
        i.e. when acceptable_sources is set and the current source is not in it.
        The default implementation sends "This command is only available in group chat." or
        "... in private chat." and breaks the run with code 1 through send_error; with
        acceptable_sources None it asserts instead.

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
        Called when the try body of CommandCaller._enter_handler raises a NoneBotException, in
        practice adapter or driver failures such as ActionFailed.
        The default implementation sends ActionFailed through send_error_render, which posts a
        user-visible error and raises BreakHandler; that bypasses the dispatch, so the run ends as
        SubCmdBreaked(1) through on_exception_parser_error. Any other NoneBotException is re-raised
        unless the entry is EnterType.External, where it is only logged.

        :param exception: NoneBotException object
        :param persona_info: PersonaInfo object
        :param send_msg: SendMsg object
        """
        if isinstance(exception, ActionFailed):
            await send_msg.send_error_render(exception)
        elif persona_info.enter_type != EnterType.External:
            raise
        else:
            logger.exception(
                "NoneBotException: {message}",
                message = str(exception),
            )

    async def on_repeater_exception(self, exception: RepeaterException, persona_info: PersonaInfo, send_msg: SendMsg) -> T | Any | None | NoReturn:
        """
        Called when the try body of CommandCaller._enter_handler raises a RepeaterException; every
        BreakHandler is one, so the framework's own break_handler calls land here too.
        The default implementation returns SubCmdBreaked(exception.code), sending the error render
        first without breaking when the exception is a BreakWithErrorMessage; any other
        RepeaterException leaves it returning None.

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
        Called when the try body of CommandCaller._enter_handler raises an Exception that is
        neither a NoneBotException nor a RepeaterException: the Handler body, the enter gates,
        check_acceptable_sources and on_debug_mode land here; BreakHandler and NoneBotException
        have their own hooks, and what those hooks or handler_exit raise leaves the dispatcher.
        The default implementation never re-raises the original exception: it logs it and posts
        a user-visible error via send_error_render (send_http_status for HTTPStatusError), then
        raises BreakHandler, which escapes the dispatch to on_exception_parser_error; handler_exit
        still runs and the run ends with its code, and a plain raise here is not re-dispatched.

        :param exception: Exception object
        :param persona_info: PersonaInfo object
        :param send_msg: SendMsg object
        """
        if isinstance(exception, httpx.HTTPStatusError):
            await send_msg.send_http_status(
                http_status = exception.response.status_code,
                message = exception.response.text
            )
        else:
            logger.exception(f"Error: {exception}")
            await send_msg.send_error_render(exception)

    async def on_exception_parser_error(self, exception: BreakHandler, persona_info: PersonaInfo, send_msg: SendMsg) -> T | Any | None | NoReturn:
        """
        Called when a BreakHandler escapes the dispatch block of CommandCaller._enter_handler -
        raised by an on_* hook or by handler_exit rather than by the Handler body, which
        on_repeater_exception consumes first.
        The default implementation returns SubCmdBreaked(exception.code): the BreakHandler is
        swallowed and nothing is sent to the chat. handler_exit has already run at this point.

        :param exception: BreakHandler object
        :param persona_info: PersonaInfo object
        :param send_msg: SendMsg object
        """
        return SubCmdBreaked(exception.code)
    
    async def on_interpreter_error(self, exception: BaseException, persona_info: PersonaInfo, send_msg: SendMsg) -> T | Any | None | NoReturn:
        """
        Called when the try body of CommandCaller._enter_handler raises a BaseException that is not
        an Exception, so no other exception hook matches it.
        The default implementation logs it with logger.exception and then raises it again.

        :param exception: BaseException object
        :param persona_info: PersonaInfo object
        :param send_msg: SendMsg object
        """
        logger.exception(f"Error: {exception}")
        raise
    
    async def on_cancel(self, persona_info: PersonaInfo, send_msg: SendMsg) -> T | Any | None | NoReturn:
        """
        Called when asyncio.CancelledError reaches the dispatch of CommandCaller._enter_handler,
        i.e. the run task was cancelled or the Handler raised it.
        The default implementation logs "<component> cancelled" at WARNING level and returns the
        SubCmdCancelled class, which becomes SubCmdCancelled(0); handler_exit still runs.

        :param persona_info: PersonaInfo object
        :param send_msg: SendMsg object
        :return: the SubCmdCancelled class, used as the result of the run
        """
        logger.warning(f"{self.component} cancelled")
        return SubCmdCancelled

    async def on_timeout(self, persona_info: PersonaInfo, send_msg: SendMsg) -> T | Any | None | NoReturn:
        """
        Called when the run exceeds storage_configs.handler_timeout; asyncio.wait_for cancels the
        task created for enter_handler before this hook is reached.
        The default implementation logs "<component> timed out" at WARNING level and returns
        SubCmdTimeout(3); handler_exit still runs.

        :param persona_info: PersonaInfo object
        :param send_msg: SendMsg object
        :return: SubCmdTimeout(3)
        """
        logger.warning(f"{self.component} timed out")
        return SubCmdTimeout(3)
    
    async def handler_exit(self, persona_info: PersonaInfo, send_msg: SendMsg) -> None:
        """
        Called in the finally of the dispatch block of CommandCaller._enter_handler, so every run
        reaches it: rejected by an enter gate or source check, served by on_debug_mode, or ended by
        any exception hook. It runs before on_exception_parser_error.
        The default implementation only logs "<component> exited" at INFO level; a BreakHandler
        raised here ends up in on_exception_parser_error.

        :param persona_info: PersonaInfo object
        :param send_msg: SendMsg object
        """
        logger.info(f"{self.component} exited")

    async def insufficient_access(self, persona_info: PersonaInfo, send_msg: SendMsg) -> T | Any | None | NoReturn:
        """
        Called by CommandCaller._enter_handler when permissions_check returned False.
        The default implementation sends "Insufficient access rights." through
        send_error_render, which breaks the run with code 1 and never returns, so the
        send_msg.break_handler() call after it is unreachable.
        Overriding it decides how a permission rejection ends the run.

        :param persona_info: User information
        :param send_msg: Send message interface
        """
        await send_msg.send_error_render("Insufficient access rights.")
        send_msg.break_handler()
    
    async def on_blacklist(self, persona_info: PersonaInfo, send_msg: SendMsg) -> T | Any | None | NoReturn:
        """
        Never invoked by the framework: there is no call site for this hook.
        The default implementation logs a WARNING naming persona_info.user_id and calls
        send_msg.break_handler(), which raises BreakHandler(0).

        :param persona_info: User information
        :param send_msg: Send message interface
        """
        logger.warning(
            "User {user_id} is in the blacklist.",
            user_id = persona_info.user_id
        )
        send_msg.break_handler()
    
    @classmethod
    def on_before_instantiate(cls):
        """
        Called by CommandCaller._make_pack at the start of a registration, before the instance
        exists and before __pre_init__ runs; it is invoked on the class.
        The default implementation does nothing.
        """
        pass
    
    def on_registed(self):
        """
        Called by CommandCaller._reg_package_instance as its last step, after the handler was
        appended to the matcher and the instance recorded in the caller's indexes; it runs before
        __post_init__ and before __time_for_registered__ is set.
        The default implementation does nothing.
        """
        pass

    def on_matcher_registered(self, matcher: Type[Matcher]) -> Type[Matcher]:
        """
        Never invoked by the current framework: there is no call site for this hook, so the
        matcher created during registration is used as is.

        The default implementation returns matcher unchanged; the return value is ignored
        anyway.

        :param matcher: The matcher that has been registered.
        """
        return matcher

    @classmethod
    def on_reg_failed(cls, exc_type, exc_val, exc_tb):
        """
        Called by CommandCaller._register with sys.exc_info() when _make_pack raised; failures
        raised later in the registration do not reach this hook.
        The default implementation re-raises the original exception and _register re-raises it
        again, so returning normally cannot rescue the registration.

        :param exc_type: Exception type
        :param exc_val: Exception value
        :param exc_tb: Exception traceback
        """
        raise
    
    @classmethod
    def on_destroy(cls):
        """
        Called by CommandCaller.destroy after the package was removed from every index and before
        the matcher is destroyed; only a still-registered package reaches it.
        The destruction path that calls it is the synchronous one - CommandCaller.adestroy calls
        on_adestroy instead. The default implementation does nothing.
        """
        pass
    
    @classmethod
    async def on_adestroy(cls):
        """
        Called by CommandCaller.adestroy after the package was removed from every index and before
        the matcher is destroyed; only a still-registered package reaches it.
        CommandCaller.destroy calls on_destroy instead. The default implementation does nothing.
        """
        pass
    
    @classmethod
    def on_duplicate_trigger(cls, other: "type[CommandPackage[Any]]"):
        """
        Called by CommandCaller._reg_triggers when a trigger (cmd or alias) already belongs to
        another package; the new package overwrites that mapping right after.
        The default implementation raises ValueError when
        storage_configs.loading.throw_on_duplicate.trigger is enabled, and otherwise logs a WARNING
        and lets the registration continue; raising aborts the registration.

        :param other: The package class that already owns this trigger
        """
        if storage_configs.loading.throw_on_duplicate.trigger:
            raise ValueError(f"Trigger {cls.package_path()} and {other.package_path()} is already registered")
        else:
            logger.warning(
                "Trigger {path} and {other_path} is already registered, this can have undesired consequences.",
                path = cls.package_path(),
                other_path = other.package_path()
            )

    @classmethod
    def on_duplicate_type(cls):
        """
        Called by CommandCaller._reg_package when this package class is already present in
        CommandCaller.classes, i.e. the same class is registered twice.
        The default implementation raises ValueError when
        storage_configs.loading.throw_on_duplicate.type is enabled, and otherwise logs a WARNING
        and lets the registration continue; raising aborts the registration.
        """
        if storage_configs.loading.throw_on_duplicate.type:
            raise ValueError(f"Handler Type {cls.package_path()} is already registered")
        else:
            logger.warning(
                "Handler type {path} is already registered, this may result in overwriting.",
                path = cls.package_path()
            )

    @classmethod
    def on_duplicate_class_name(cls, other: "type[CommandPackage[Any]]"):
        """
        Called by CommandCaller._reg_package when another package is already registered under the
        same __name__ in CommandCaller.class_names.
        The default implementation raises ValueError when
        storage_configs.loading.throw_on_duplicate.class_name is enabled, and otherwise logs a
        WARNING and lets the new class take the name; raising aborts the registration.

        :param other: The package class that already holds this class name
        """
        if storage_configs.loading.throw_on_duplicate.class_name:
            raise ValueError(f"Handler class name {cls.package_path()} and {other.package_path()} is already registered")
        else:
            logger.warning(
                "Handler class name {self_path} and {other_path} is already registered, this may result in overwriting.",
                self_path = cls.package_path(),
                other_path = other.package_path()
            )

    @classmethod
    def on_duplicate_component(cls, other: "type[CommandPackage[Any]]"):
        """
        Called by CommandCaller._reg_package when another package already reports the same
        component string, i.e. the human-readable name is taken; the new package overwrites the
        mapping right after.
        The default implementation raises ValueError when
        storage_configs.loading.throw_on_duplicate.component is enabled, and otherwise logs a
        WARNING and lets the registration continue; raising aborts the registration.

        :param other: The package class that already holds this component name
        """
        if storage_configs.loading.throw_on_duplicate.component:
            raise ValueError(f"Component {cls.package_path()} and {other.package_path()} is already registered")
        else:
            logger.warning(
                "Component {self_path} and {other_path} is already registered, this may result in overwriting.",
                self_path = cls.package_path(),
                other_path = other.package_path(),
            )

    @classmethod
    def on_duplicate_handler(cls):
        """
        Called by CommandCaller._reg_package on the instance when this package class is already
        present in CommandCaller.commands, i.e. the same class is registered twice; the previous
        instance and matcher are overwritten and the old matcher is not destroyed.
        The default implementation raises ValueError when
        storage_configs.loading.throw_on_duplicate.handler is enabled, and otherwise logs a
        WARNING and lets the registration continue; raising aborts the registration.
        """
        if storage_configs.loading.throw_on_duplicate.handler:
            raise ValueError(f"Handler {cls.package_path()} is already registered")
        else:
            logger.warning(
                "Handler {handler} is already registered, this may result in overwriting.",
                handler = cls.package_path(),
            )

    @classmethod
    def on_duplicate_matcher(cls, matcher: Type[Matcher]):
        """
        Called by CommandCaller._reg_package when a matcher is already registered for this package
        class, i.e. the registered matcher is about to be replaced by matcher.
        The default implementation raises ValueError when
        storage_configs.loading.throw_on_duplicate.matcher is enabled, and otherwise logs a
        WARNING and lets the registration continue; raising aborts the registration.

        :param matcher: The matcher that would replace the registered one
        """
        if storage_configs.loading.throw_on_duplicate.matcher:
            raise ValueError(f"The {cls.package_path()} Matcher {repr(matcher)} is re-registered.")
        else:
            logger.warning(
                "The {handler} matcher {matcher} is already registered, this may result in overwriting.",
                handler = cls.package_path(),
                matcher = repr(matcher)
            )

    async def on_framework_startup(self):
        """
        Broadcast by CommandCaller.on_startup, i.e. on the NoneBot on_startup driver event, to
        every registered package concurrently.
        The default implementation does nothing; exceptions it raises are swallowed by
        asyncio.gather(..., return_exceptions=True) and never stop the startup.
        """
        pass

    async def on_framework_shutdown(self):
        """
        Broadcast by CommandCaller.on_shutdown, i.e. on the NoneBot on_shutdown driver event, to
        every registered package concurrently.
        It runs before close_packages() cancels listeners, running handlers, pipes and statuses,
        so it is the last moment to talk to other handlers; exceptions are swallowed by
        asyncio.gather(..., return_exceptions=True) and the default implementation does nothing.
        """
        pass

    async def on_bot_connect(self, bot: Bot):
        """
        Broadcast by CommandCaller.on_bot_connect, i.e. on the NoneBot on_bot_connect driver event,
        to every registered package concurrently, after the external-trigger callback for
        bot.self_id was registered.
        The default implementation does nothing and exceptions are swallowed by asyncio.gather.

        :param bot: The bot object
        """
        pass

    async def on_bot_disconnect(self, bot: Bot):
        """
        Broadcast by CommandCaller.on_bot_disconnect, i.e. on the NoneBot on_bot_disconnect driver
        event, to every registered package concurrently, after the external-trigger callback for
        bot.self_id was unregistered.
        The default implementation does nothing and exceptions are swallowed by asyncio.gather.

        :param bot: The bot object
        """
        pass
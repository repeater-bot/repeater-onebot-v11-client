import sys
import time
import uuid
import asyncio
from croniter import croniter
from datetime import datetime
from .package import CommandPackage
from ..assist import (
    PersonaInfo,
    SendMsg,
    SendingTarget,
    Namespace,
    Variables
)
from ..cmd_info import CmdTypes
from ..client_configs import storage_configs
from ..exceptions import *
from nonebot.exception import NoneBotException
from nonebot import get_driver
from typing import (
    Any,
    Type,
    Callable,
    Awaitable,
    TypeVar,
    Union,
    NoReturn,
    Generator
)
from nonebot import on_command, on_message
from nonebot import get_driver
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, Message
from .listen_type import ListenType
from nonebot import logger
from .running_package import RunningPackage
from .sub_cmd_exit import SubCmdBreaked, SubCmdExit
from .external_trigger import register_external_trigger, et_server

T_Handler_Result = TypeVar("T_Handler_Result")

class CommandCaller:
    commands: dict[Type[CommandPackage[Any]], CommandPackage[Any]] = {}
    triggers: dict[str | tuple[str, ...], Type[CommandPackage[Any]]] = {}
    class_names: dict[str, Type[CommandPackage[Any]]] = {}
    classes: set[type[CommandPackage[Any]]] = set()
    types: dict[CmdTypes, list[Type[CommandPackage[Any]]]] = {}
    matchers: dict[Type[CommandPackage[Any]], Type[Matcher]] = {}
    components: dict[str, Type[CommandPackage[Any]]] = {}

    runnings: dict[uuid.UUID, RunningPackage] = {}
    running_map: dict[Namespace, set[uuid.UUID]] = {}
    running_lock = asyncio.Lock()

    variables: dict[Namespace, Variables[str]] = {}
    variable_lock = asyncio.Lock()

    listen_message_tasks: dict[Namespace, set[asyncio.Future[PersonaInfo]]] = {}
    listen_lock: asyncio.Lock = asyncio.Lock()
    et_server_task: asyncio.Task | None = None

    @classmethod
    async def run_et_server(cls):
        """Run the external trigger server."""
        logger.info(
            "Starting external trigger server..."
        )
        await et_server.serve()

    @classmethod
    async def on_startup(cls):
        """Run on startup."""
        logger.info(
            "startup..."
        )

        if storage_configs.external_trigger_server.enabled:
            cls.et_server_task = asyncio.create_task(
                cls.run_et_server()
            )
        else:
            logger.info(
                "External trigger server is disabled."
            )

        tasks: list[asyncio.Task] = []
        for command in cls.commands.values():
            tasks.append(
                asyncio.create_task(
                    command.on_framework_startup()
                )
            )
        await asyncio.gather(*tasks)

    @classmethod
    async def on_shutdown(cls):
        """Run on shutdown."""
        logger.info(
            "shutdown..."
        )
        tasks: list[asyncio.Task] = []
        for command in cls.commands.values():
            tasks.append(
                asyncio.create_task(
                    command.on_framework_shutdown()
                )
            )
        await asyncio.gather(*tasks)
        
        for listening in cls.listen_message_tasks.values():
            for task in listening:
                task.cancel()

    @classmethod
    async def on_bot_connect(cls, bot: Bot):
        """
        Run on bot connect.
        """
        logger.info(
            "bot {bot_id} connect...",
            bot_id = bot.self_id
        )
        async def external_trigger_callback(handler: str, event: MessageEvent, args: Message):
            nonlocal cls, bot
            package = cls.match_trigger_or_component(handler)
                
            messages, result = await cls._external_enter(
                package = package,
                bot = bot,
                event = event,
                args = args,
            )

            retcode: int = 0

            if isinstance(result, SubCmdExit):
                retcode = result.code

            return messages, retcode

        
        register_external_trigger.register(
            bot.self_id,
            external_trigger_callback
        )

        tasks: list[asyncio.Task] = []
        for command in cls.commands.values():
            tasks.append(
                asyncio.create_task(
                    command.on_bot_connect(bot)
                )
            )
        await asyncio.gather(*tasks)

    @classmethod
    async def on_bot_disconnect(cls, bot: Bot):
        """bot disconnect..."""
        logger.info(
            "bot {bot_id} disconnect...",
            bot_id = bot.self_id
        )

        register_external_trigger.unregister(bot.self_id)

        tasks: list[asyncio.Task] = []
        for command in cls.commands.values():
            tasks.append(
                asyncio.create_task(
                    command.on_bot_disconnect(bot)
                )
            )
        await asyncio.gather(*tasks)

    @staticmethod
    def cmd_prefixs() -> set[str]:
        return get_driver().config.command_start

    @staticmethod
    def delimiters() -> set[str]:
        return get_driver().config.command_sep
    
    @classmethod
    def match_trigger(cls, trigger: str | tuple[str, ...]) -> Type[CommandPackage[Any]]:
        return cls.triggers[trigger]

    @classmethod
    def match_component(cls, component: str) -> Type[CommandPackage[Any]]:
        return cls.components[component]

    @classmethod
    def cancel(cls, namespace: Namespace, task: uuid.UUID | RunningPackage):
        if isinstance(task, uuid.UUID):
            task_id = task
        elif isinstance(task, RunningPackage):
            task_id = task.task_id
        else:
            raise TypeError("task must be uuid.UUID or RunningPackage")

        if namespace in cls.running_map:
            if task_id in cls.running_map[namespace]:
                if task_id in cls.runnings:
                    cls.running_map[namespace].remove(task_id)

    @classmethod
    async def has_running_task(cls, namespace: Namespace, task: uuid.UUID) -> bool:
        async with cls.running_lock:
            return task in cls.running_map.get(namespace, set())

    @classmethod
    async def get_runnings(cls, namespace: Namespace) -> set[RunningPackage]:
        async with cls.running_lock:
            runnings = cls.running_map.get(namespace, set())
            return {cls.runnings[i] for i in runnings}
    
    @classmethod
    async def get_user_runnings(cls, namespace: Namespace) -> list[RunningPackage]:
        async with cls.running_lock:
            return [cls.runnings[uuid] for uuid in cls.running_map.get(namespace, set())]

    @classmethod
    def match_trigger_or_component(cls, string: str | tuple[str, ...]) -> Type[CommandPackage[Any]]:
        if isinstance(string, str):
            package: type[CommandPackage] | None = None
            try:
                package = CommandCaller.match_component(string)
            except KeyError:
                for prefix in CommandCaller.cmd_prefixs():
                    if string.startswith(prefix):
                        package = CommandCaller.match_trigger(
                            string.removeprefix(prefix)
                        )
                        break
            if package is None:
                raise KeyError(f"Unknown component: {string}")
            return package
        elif isinstance(string, tuple):
            return cls.match_trigger(string)
        else:
            raise TypeError(f"Unsupported type: {type(string).__name__}")
    
    @classmethod
    def get_instance(cls, package: Type[CommandPackage[T_Handler_Result]]) -> CommandPackage[T_Handler_Result]:
        """
        Get the instance of the command package.

        :param package: The command package.
        :return: The instance of the command package.
        """
        return cls.commands[package]

    @classmethod
    def get_command_handler(cls, package: CommandPackage[T_Handler_Result], matcher: Type[Matcher]) -> Callable[[Bot, MessageEvent, Message], Awaitable[T_Handler_Result | Any | SubCmdBreaked | None | NoReturn]]:
        """
        Get the command handler.

        :param package: The command package.
        :param matcher: The matcher.
        :return: The command handler.
        """
        async def command_handler(bot: Bot, event: MessageEvent, args: Message = CommandArg()) -> T_Handler_Result | Any | SubCmdBreaked | None | NoReturn:
            nonlocal package, matcher
            logger.info(
                "Run command handler: {name}",
                name = package.component,
            )
            task_id = uuid.uuid4()
            persona_info ,send_msg = await package.command_enter(
                bot,
                event,
                args,
                matcher,
                task_id
            )
            return await cls.run_handle(
                task_id,
                package,
                persona_info,
                send_msg
            )
        return command_handler
    
    @classmethod
    def get_message_handler(cls, package: CommandPackage[T_Handler_Result], matcher: Type[Matcher]) -> Callable[[Bot, MessageEvent], Awaitable[T_Handler_Result | Any | SubCmdBreaked | None | NoReturn]]:
        """
        Get the message handler.

        :param package: The command package.
        :param matcher: The matcher.
        :return: The message handler.
        """
        async def message_handler(bot: Bot, event: MessageEvent) -> T_Handler_Result | Any | SubCmdBreaked | None | NoReturn:
            nonlocal package, matcher
            logger.info(
                "Run message handler: {name}",
                name = package.component,
            )
            task_id = uuid.uuid4()
            persona_info ,send_msg = await package.message_enter(
                bot,
                event,
                matcher,
                task_id
            )
            return await cls.run_handle(
                task_id,
                package,
                persona_info,
                send_msg
            )
        return message_handler
    
    @classmethod
    async def wait_message(cls, namespace: Namespace) -> PersonaInfo:
        """
        Wait for the message.

        :param package: The command package.
        :param task: The task.
        :return: None
        """
        future = await cls.message_future(namespace)
        result = await future
        return result
    
    @classmethod
    async def message_future(cls, namespace: Namespace) -> asyncio.Future[PersonaInfo]:
        """
        Create a Future to wait for the message.

        :param package: The command package.
        :param task: The task.
        :return: None
        """
        loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
        future: asyncio.Future[PersonaInfo] = loop.create_future()
        async with cls.listen_lock:
            logger.info(
                "Create Wait {namespace} Message Task: {future}",
                namespace = namespace.namespace_str,
                future = repr(future),
            )
            cls.listen_message_tasks.setdefault(namespace, set()).add(future)
        return future

    @classmethod
    async def cancel_wait_message(cls, namespace: Namespace) -> bool:
        """
        Cancel the wait message.

        :param package: The command package.
        :param task: The task.
        :return: None
        """
        async with cls.listen_lock:
            logger.info(
                "Cancel Wait {namespace} Message Task",
                namespace = namespace.namespace_str,
            )
            if namespace in cls.listen_message_tasks:
                for future in cls.listen_message_tasks[namespace]:
                    future.cancel()
                del cls.listen_message_tasks[namespace]
                logger.info(
                    "Cancel Wait {namespace} Message Task Success",
                    namespace = namespace.namespace_str,
                )
                return True

        return False

    @classmethod
    async def run_handle(
        cls,
        task_id: uuid.UUID,
        package: CommandPackage[T_Handler_Result],
        persona_info: PersonaInfo,
        send_msg: SendMsg,
        debug_mode: bool | None = None,
        created: asyncio.Future[RunningPackage[T_Handler_Result]] | None = None
    ) -> T_Handler_Result | Any | SubCmdBreaked | None | NoReturn:
        try:
            task = asyncio.create_task(
                cls.enter_handler(
                    task_id = task_id,
                    package = package,
                    persona_info = persona_info,
                    send_msg = send_msg,
                    debug_mode = debug_mode,
                )
            )
            running: RunningPackage[T_Handler_Result] = RunningPackage(
                task_id = task_id,
                start_time = time.time_ns(),
                start_monotonic_time = time.perf_counter_ns(),
                package = package,
                matcher = send_msg.matcher,
                persona_info = persona_info,
                send_msg = send_msg,
                task = task
            )

            async with cls.running_lock:
                cls.runnings[task_id] = running
                cls.running_map.setdefault(
                    persona_info.namespace,
                    set()
                ).add(task_id)
        except Exception as e:
            if created is not None:
                created.set_exception(e)
            raise

        if created is not None:
            created.set_result(running)

        try:
            result = await running
            return result
        finally:
            async with cls.running_lock:
                cls.runnings.pop(task_id, None)
                if persona_info.namespace in cls.running_map:
                    user_running = cls.running_map[persona_info.namespace]
                    user_running.discard(task_id)
                    if not user_running:
                        cls.running_map.pop(persona_info.namespace)
    
    @classmethod
    async def enter_handler(
        cls,
        task_id: uuid.UUID,
        package: CommandPackage[T_Handler_Result],
        persona_info: PersonaInfo,
        send_msg: SendMsg,
        debug_mode: bool | None = None,
    ) -> T_Handler_Result | Any:
        """
        Enter the message handler.

        :param task_id: The task id.
        :param package: The command package.
        :param persona_info: The persona info.
        :param send_msg: The send message function.
        :param created: The running package created future.
        :param debug_mode: The debug mode.
        :return: The result of the message handler.
        """
        if debug_mode is None:
            if send_msg.is_debug_mode:
                debug_mode = True
            else:
                debug_mode = False
        
        result = await cls._enter_hander(
            task_id,
            package,
            persona_info,
            send_msg,
            debug_mode,
        )
        if isinstance(result, type):
            if issubclass(result, SubCmdBreaked):
                result = result()

        if isinstance(result, SubCmdExit):
            result_code = result.code
        else:
            result_code = 0
        
        logger.info(
            "Handler {handler}[{task_id}] result: {result}({type}), return code: {code}, debug: {debug_mode}",
            handler = package.component,
            task_id = task_id,
            result = repr(result),
            code = result_code,
            type = type(result).__name__,
            debug_mode = debug_mode
        )
        return result
    
    @classmethod
    async def _enter_hander(
        cls,
        task_id: uuid.UUID,
        package: CommandPackage[T_Handler_Result],
        persona_info: PersonaInfo,
        send_msg: SendMsg,
        debug_mode: bool = False,
    ) -> T_Handler_Result | Any:
        """
        Enter the message handler.

        :param task_id: The task id.
        :param created: The running package created future.
        :param package: The command package.
        :param persona_info: The persona info.
        :param send_msg: The send message function.
        :param debug_mode: Whether to enable debug mode.
        :return: The result of the message handler.
        """
        try:
            try:
                logger.info(
                    "Enter {command}[{task_id}] from message: {message_id} ({enter_mode} Mode)",
                    command = package.component,
                    task_id = task_id,
                    message_id = persona_info.message_id,
                    enter_mode = persona_info.enter_type.name,
                )

                if not await package.enter_check(persona_info, send_msg):
                    logger.warning(
                        "Enter check blocked: {name}[{task_id}]",
                        name = package.component,
                        task_id = task_id,
                    )
                    send_msg.break_handler()

                if not await package.permissions_check(persona_info, send_msg):
                    logger.warning(
                        "Command {name}[{task_id}] from message {message_id} has insufficient access",
                        name = package.component,
                        message_id = persona_info.message_id,
                        task_id = task_id,
                    )
                    send_msg.break_handler()
                
                if not await cls.check_acceptable_sources(package, persona_info):
                    return await package.on_unacceptable_source(persona_info, send_msg)
                
                if package.super_permissions and not persona_info.has_super_permissions:
                    return await package.insufficient_access(persona_info, send_msg)

                if debug_mode:
                    return await package.on_debug_mode(persona_info, send_msg)
                
                task = asyncio.create_task(
                    package.enter_handler(
                        persona_info = persona_info,
                        send_msg = send_msg
                    )
                )
                return await asyncio.wait_for(
                    task,
                    timeout = storage_configs.handler_timeout,
                )
            
            except asyncio.CancelledError:
                return await package.on_cancel(persona_info, send_msg)
            except asyncio.TimeoutError:
                return await package.on_timeout(persona_info, send_msg)
            except NoneBotException as e:
                return await package.on_nonebot_exception(e, persona_info, send_msg)
            except RepeaterException as e:
                return await package.on_repeater_exception(e, persona_info, send_msg)
            except Exception as e:
                return await package.on_error(e, persona_info, send_msg)
            except BaseException as e:
                return await package.on_interpreter_error(e, persona_info, send_msg)
            finally:
                await package.handler_exit(persona_info, send_msg)
        except BreakHandler as e:
            return SubCmdBreaked(e.code)

    @classmethod
    async def timed_scheduling(
        cls,
        package: Type[CommandPackage[T_Handler_Result]] | CommandPackage[T_Handler_Result],
        cron: str,
        persona_info: PersonaInfo,
        send_msg: SendMsg | None = None,
        debug_mode: bool | None = None
    ):
        try:
            cron_iter = croniter(
                expr_format = cron,
                start_time = datetime.now()
            )
        except ValueError as e:
            raise ValueError(f"Invalid cron expression: {e}") from e
        while True:
            now = datetime.now()
            next_time = cron_iter.get_next(datetime)
            delta = next_time - now
            logger.info(
                "{command} next runtime is {next_time}(wait {delta} seconds)",
                command = package.component,
                next_time = next_time,
                delta = delta.total_seconds()
            )
            await asyncio.sleep(delta.total_seconds())
            await cls.horizontal_call(
                package = package,
                persona_info = persona_info,
                send_msg = send_msg,
                debug_mode = debug_mode
            )
    
    @classmethod
    async def horizontal_call(
        cls,
        package: Type[CommandPackage[T_Handler_Result]] | CommandPackage[T_Handler_Result],
        persona_info: PersonaInfo,
        send_msg: SendMsg | None = None,
        debug_mode: bool | None = None
    ) -> T_Handler_Result | Any:
        """
        Horizontal call handler

        :param package: CommandPackage
        :param persona_info: PersonaInfo
        :param send_msg: SendMsg
        :param debug_mode: run handler at debug mode
        :return: Handler result
        """
        if isinstance(package, CommandPackage):
            package_instance = package
        elif isinstance(package, type) and issubclass(package, CommandPackage):
            package_instance: CommandPackage[T_Handler_Result] = cls.commands[package]
        else:
            raise TypeError("package must be CommandPackage or subclass of CommandPackage")
        
        task_id = uuid.uuid4()
        persona_info_copy, send_msg_copy = await package_instance.horizontal_enter(persona_info, send_msg, task_id)
        return await cls.run_handle(
            task_id = task_id,
            package = package_instance,
            persona_info = persona_info_copy,
            send_msg = send_msg_copy,
            debug_mode = debug_mode
        )

    @classmethod
    async def horizontal_enter_wait_created(
        cls,
        package: Type[CommandPackage[T_Handler_Result]] | CommandPackage[T_Handler_Result],
        persona_info: PersonaInfo,
        send_msg: SendMsg | None = None,
        debug_mode: bool | None = None
    ) -> RunningPackage[T_Handler_Result]:
        """
        Horizontal call handler and waiting for the running package to created.

        :param package: CommandPackage
        :param persona_info: PersonaInfo
        :param send_msg: SendMsg
        """
        if isinstance(package, CommandPackage):
            package_instance = package
        elif isinstance(package, type) and issubclass(package, CommandPackage):
            package_instance: CommandPackage[T_Handler_Result] = cls.commands[package]
        else:
            raise TypeError("package must be CommandPackage or subclass of CommandPackage")
        
        task_id = uuid.uuid4()
        persona_info_copy, send_msg_copy = await package_instance.horizontal_enter(persona_info, send_msg, task_id)
        loop = asyncio.get_running_loop()
        created: asyncio.Future[RunningPackage[T_Handler_Result]] = loop.create_future()
        asyncio.create_task(
            cls.run_handle(
                task_id = task_id,
                package = package_instance,
                persona_info = persona_info_copy,
                send_msg = send_msg_copy,
                debug_mode = debug_mode,
                created = created,
            )
        )
        return await created

    @classmethod
    async def _external_enter(
        cls,
        package: Type[CommandPackage[T_Handler_Result]] | CommandPackage[T_Handler_Result],
        bot: Bot,
        event: MessageEvent,
        args: Message,
        debug_mode: bool | None = None
    ) -> tuple[list[Message], T_Handler_Result | Any]:
        """
        Horizontal call handler and waiting for the running package to created.

        :param package: CommandPackage
        :param persona_info: PersonaInfo
        :param send_msg: SendMsg
        """
        if isinstance(package, CommandPackage):
            package_instance = package
        elif isinstance(package, type) and issubclass(package, CommandPackage):
            package_instance: CommandPackage[T_Handler_Result] = cls.commands[package]
        else:
            raise TypeError("package must be CommandPackage or subclass of CommandPackage")
        
        task_id = uuid.uuid4()
        persona_info, send_msg = await package_instance.external_enter(
            bot = bot,
            event = event,
            args = args,
            task_id = task_id
        )

        outputs: list[Message] = []
        async def get_message_outputs(message: Message, target: SendingTarget):
            nonlocal outputs
            outputs.append(message)

        send_msg_copy = send_msg.copy(
            send_hook = get_message_outputs
        )

        result = await cls.run_handle(
            task_id = task_id,
            package = package_instance,
            persona_info = persona_info,
            send_msg = send_msg_copy,
            debug_mode = debug_mode
        )
        return outputs, result

    
    @staticmethod
    async def check_acceptable_sources(package: CommandPackage[T_Handler_Result], persona_info: PersonaInfo) -> bool:
        """
        Check if the persona is allowed to call the command

        :param package: CommandPackage
        :param persona_info: PersonaInfo
        :return: True if the persona is allowed to call the command, False otherwise
        """
        if package.acceptable_sources is None:
            return True
        return persona_info.source in package.acceptable_sources

    @classmethod
    def register(
        cls,
        package: Type[CommandPackage[T_Handler_Result]]
    ) -> Type[CommandPackage[T_Handler_Result]]:
        """
        Register a command

        :param package: CommandPackage
        :return: CommandPackage
        """
        return cls._register(package)

    @classmethod
    def register_with_args(
        cls,
        *args,
        **kwargs
    ) -> Callable[[Type[CommandPackage[T_Handler_Result]]], type[CommandPackage[T_Handler_Result]]]:
        """
        Register a command with args

        :param args: args
        :param kwargs: kwargs
        :return: CommandPackage
        """
        def _decorator(package: Type[CommandPackage[T_Handler_Result]]) -> Type[CommandPackage[T_Handler_Result]]:
            nonlocal args, kwargs
            return cls._register(package, *args, **kwargs)
        return _decorator
    
    @classmethod
    def _register(cls, package: Type[CommandPackage[T_Handler_Result]], *args: Any, **kwargs: Any) -> Type[CommandPackage[T_Handler_Result]]:
        """
        Register a command

        :param package: CommandPackage Type
        :return: CommandPackage Type
        """
        if package.enabled:
            register_start_time = time.perf_counter_ns()
            try:
                package_instance, matcher, handler = cls._make_pack(package, *args, **kwargs)
            except:
                package.on_reg_failed(*sys.exc_info())
            
            cls._reg_package_instance(
                package = package,
                package_instance = package_instance,
                matcher = matcher,
                handler = handler
            )
            package_instance.__post_init__()
            package_instance.__time_for_registered__ = time.time_ns()
            register_end_time = time.perf_counter_ns()
            package_instance.__time_for_registered_monotonic__ = register_end_time

            logger.info(
                "Register command {name} done, cost {cost:.3f} ms",
                name = package_instance.component,
                cost = (register_end_time - register_start_time) / 1e6
            )
        return package
    
    @classmethod
    def _make_pack(
        cls,
        package: Type[CommandPackage[T_Handler_Result]],
        *args: Any,
        **kwargs: Any,
    )  -> tuple[
        CommandPackage[T_Handler_Result], # package_instance
        type[Matcher], # matcher
        Union[
        # Command Handler
            Callable[
                [Bot, MessageEvent, Message],
                Awaitable[T_Handler_Result | Any | SubCmdBreaked | None]
            ],
            # Message Handler
            Callable[
                [Bot, MessageEvent],
                Awaitable[T_Handler_Result | Any | SubCmdBreaked | None]
            ]
        ]
    ]:
        package.on_before_instantiate()

        package_raw_new = package.__new__
        def package_new(cls: Type[CommandPackage[T_Handler_Result]]):
            nonlocal package_raw_new
            package_instance = package_raw_new(cls)
            package_instance.__pre_init__()
            return package_instance
        package.__new__ = package_new
        package.__raw_new__ = package_raw_new

        package_instance = package(*args, **kwargs)
        package_instance.__time_for_created__ = time.time_ns()
        package_instance.__time_for_created_monotonic__ = time.perf_counter_ns()
            
        match package_instance.listen_type:
            case ListenType.Command:
                matcher = cls._create_command_matcher(package_instance)
                if storage_configs.log_registed_handler_name:
                    logger.info(
                        "Register Command Handler: {name}",
                        name = package_instance.component
                    )
                handler = cls.get_command_handler(package_instance, matcher)
            case ListenType.Message:
                matcher = cls._create_message_matcher(package_instance)
                if storage_configs.log_registed_handler_name:
                    logger.info(
                        "Register Message Handler: {name}",
                        name = package_instance.component
                    )
                handler = cls.get_message_handler(package_instance, matcher)
            case _:
                raise ValueError(f"{package_instance.listen_type} is not supported")
        return package_instance, matcher, handler
    
    @classmethod
    def _reg_package_instance(
        cls,
        package: Type[CommandPackage[T_Handler_Result]],
        package_instance: CommandPackage[T_Handler_Result],
        matcher: Type[Matcher],
        handler: Union[
            # Command Handler
            Callable[
                [Bot, MessageEvent, Message],
                Awaitable[T_Handler_Result | Any | SubCmdBreaked | None]
            ],
            # Message Handler
            Callable[
                [Bot, MessageEvent],
                Awaitable[T_Handler_Result | Any | SubCmdBreaked | None]
            ]
        ]
    ) -> None:
        matcher.append_handler(handler)
        cls._reg_package(
            package = package,
            package_instance = package_instance,
            matcher = matcher
        )
        package_instance.on_registed()
    
    @classmethod
    def _unreg_package_instance(
        cls,
        package: Type[CommandPackage[T_Handler_Result]],
    ) -> tuple[
        CommandPackage[Any],
        type[Matcher]
    ]:
        package_instance: CommandPackage[Any] = cls.commands.pop(package)
        main_trigger: Type[CommandPackage[Any]] = cls.triggers.pop(package.cmd)
        types: list[Type[CommandPackage[Any]]] = cls.types.pop(package_instance.cmd_type)
        triggers: list[Type[CommandPackage[T_Handler_Result]]] = []
        components: Type[CommandPackage[Any]] = cls.components.pop(package_instance.component)
        if package_instance.aliases is not None:
            triggers = [
                cls.triggers.pop(trigger)
                for trigger in
                cls.get_package_aliases(package_instance)
            ]
        
        matcher: Type[Matcher] = cls.matchers.pop(package)

        return (
            package_instance,
            matcher
        )

    
    @classmethod
    def _reg_package(
        cls,
        package: Type[CommandPackage[T_Handler_Result]],
        package_instance: CommandPackage[T_Handler_Result],
        matcher: Type[Matcher]
    ) -> None:
        """
        Register package to resource pool
        """
        if package in cls.commands:
            package_instance.on_duplicate_handler()
        cls.commands[package] = package_instance

        if package in cls.matchers:
            package.on_duplicate_matcher(matcher)
        cls.matchers[package] = matcher

        cls._reg_cmd_types(package_instance.cmd_type, package)

        if package in cls.classes:
            package.on_duplicate_type()

        if package_instance.component in cls.components:
            package_instance.on_duplicate_component(
                cls.get_instance(
                    cls.components[package_instance.component]
                )
            )
        cls.components[package_instance.component] = package
        
        if package.__name__ in cls.class_names:
            package.on_duplicate_class_name(
                cls.get_instance(
                    cls.class_names[package.__name__]
                )
            )
        cls.class_names[package.__name__] = package
        
        if package_instance.listen_type == ListenType.Command:
            cls._reg_triggers(package_instance.cmd, package)
            if package_instance.aliases:
                for trigger in cls.get_package_aliases(package_instance):
                    cls._reg_triggers(trigger, package)
        
        if storage_configs.loading.recommended_class_name_is_trigger:
            if package.aliases is not None:
                commands = cls.get_package_aliases(package_instance)
            else:
                commands = set()

            if hasattr(package, "cmd"):
                commands.add(package.cmd)

            if package.__name__ not in commands:
                logger.warning(
                    "Recommended class name is trigger, but {class_name} is not",
                    class_name = package_instance.component
                )
    
    @classmethod
    def _reg_cmd_types(cls, cmd_type: CmdTypes, package: Type[CommandPackage[T_Handler_Result]]) -> None:
        """
        Register package to types pool
        """
        types_list: list[Type[CommandPackage[Any]]] = cls.types.setdefault(cmd_type, [])
        types_list.append(package)
    
    @classmethod
    def _reg_triggers(cls, trigger: str | tuple[str, ...], package: Type[CommandPackage[T_Handler_Result]]) -> None:
        """
        Register package to triggers pool
        """
        if trigger in cls.triggers:
            package.on_duplicate_trigger(trigger)
        cls.triggers[trigger] = package
    
    @classmethod
    def registed_info_table(cls) -> Generator[str, None, None]:
        """
        Get registed info table
        """
        total = len(cls.commands)
        yield f"Registed {total} commands"
        yield f"Registed {len(cls.triggers)} triggers"
        yield f"Registed {len(cls.components)} components"
        
        if total > 0:
            yield "Repeater:"
            for cmd_type, packages in cls.types.items():
                yield f"  {cmd_type}({len(packages) / total:.2%})"
                for package in packages:
                    package_instance = cls.commands[package]
                    yield f"    {package_instance.component}"

    @classmethod
    def log_registed_info(cls) -> None:
        """
        Log registed info
        """
        for info in cls.registed_info_table():
            logger.info(
                "{info}",
                info = info
            )
    
    @classmethod
    def destroy(cls, package: Type[CommandPackage[T_Handler_Result]]) -> None:
        """
        Destroy a Handler

        :param package: The package of the Handler
        """
        if package in cls.commands:
            package_instance, matcher = cls._unreg_package_instance(package)

            logger.info(
                "Destroy Handler: {name}",
                name = package_instance.component
            )
            
            package_instance.on_destroy()
            matcher.destroy()
    
    @classmethod
    async def adestroy(cls, package: Type[CommandPackage[T_Handler_Result]]) -> None:
        """
        Destroy a Handler on an async context
        
        :param package: The package of the Handler
        """
        if package in cls.commands:
            package_instance: CommandPackage[Any] = cls.commands.pop(package)
            matcher: Type[Matcher] = cls.matchers.pop(package)

            logger.info(
                "Async Destroy command: {name}",
                name = package_instance.component
            )
            
            await package_instance.on_adestroy()
            matcher.destroy()

    @staticmethod
    def get_package_aliases(package: CommandPackage) -> set[str | tuple[str, ...]]:
        """
        Get the aliases of a package

        :param package: The package of the Handler
        :return: The aliases
        """
        aliases: set[str | tuple[str, ...]]
        if isinstance(package.aliases, set):
            aliases = package.aliases.copy()
        elif package.aliases is not None:
            aliases = set(package.aliases)
        else:
            aliases = set()
        
        if storage_configs.loading.component_is_trigger:
            aliases.add(package.component)

        return aliases
    
    @classmethod
    def _create_command_matcher(cls, package: CommandPackage) -> Type[Matcher]:
        """
        Create a matcher for a package

        :param package: The package of the Handler
        :return: The matcher
        """
        if package.listen_type == ListenType.Command:
            matcher = on_command(
                cmd = package.cmd,
                rule = package.rule,
                aliases = cls.get_package_aliases(package),
                force_whitespace = package.force_whitespace,
                permission = package.permission,
                handlers = package.handlers,
                temp = package.temp,
                expire_time = package.expire_time,
                priority = package.priority,
                block = package.block,
                state = package.state,
            )
            return matcher
        else:
            raise ValueError(f"Unknown listen type: {package.listen_type}")
    
    @classmethod
    def _create_message_matcher(cls, package: CommandPackage) -> Type[Matcher]:
        """
        Create a matcher for a package

        :param package: The package of the Handler
        :return: The matcher
        """
        if package.listen_type == ListenType.Message:
            matcher = on_message(
                rule = package.rule,
                permission = package.permission,
                handlers = package.handlers,
                temp = package.temp,
                expire_time = package.expire_time,
                priority = package.priority,
                block = package.block,
                state = package.state,
            )
            return matcher
        else:
            raise ValueError(f"Unknown listen type: {package.listen_type}")
    
    @classmethod
    async def report_message(cls, persona_info: PersonaInfo):
        """
        Report a new message for processing.
        """
        namespace = persona_info.namespace
        if namespace in cls.listen_message_tasks:
            async with cls.listen_lock:
                futures: set[asyncio.Future[PersonaInfo]] = cls.listen_message_tasks.pop(namespace)
                for future in futures:
                    future.set_result(persona_info)
            logger.info(
                "{namespace} Message Wait Finished",
                namespace = namespace.namespace_str,
            )
                
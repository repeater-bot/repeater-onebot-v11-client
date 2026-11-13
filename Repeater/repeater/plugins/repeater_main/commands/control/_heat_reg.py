import sys
from typing import Any
from ...assist import PersonaInfo, SendMsg
from ...cmd_info import CmdTypes
from ...command_register import(
    CommandCaller,
    CommandPackage
)
from ...logger import logger
from ._heat_load import (
    find_commands_anchor,
    split_module_name
)
from ._heat_unload import package_triggers

def absolute_parts(package_name: str, parts: list[str]) -> list[str]:
    """The full dotted parts of the class path.

    Both forms are accepted: relative to the commands package
    (``control.some_file.SomeClass``) and already absolute
    (``<prefix>.commands.control.some_file.SomeClass``). A relative path is
    anchored on ``package_name``, so neither form can reach outside it.

    :param package_name: the dotted name of the commands package
    :param parts: the argument split on dots
    :return: the absolute parts
    """
    base = package_name.split(".")
    if parts[: len(base)] == base:
        return parts
    return base + parts

def find_module(package_name: str, parts: list[str]) -> tuple[Any, list[str]] | None:
    """Find the longest already-imported module prefix of ``parts``.

    Nothing is imported and nothing touches the filesystem: a class path only
    resolves when its module is already in ``sys.modules``, which is exactly the
    state heatLoad leaves behind. The search floor is the commands package
    itself, so a prefix above it is never considered. The whole path is tried
    first, so passing a module instead of a class is reported as such rather
    than as "not found".

    :param package_name: the dotted name of the commands package
    :param parts: the absolute parts of the class path
    :return: ``(module, attributes left to walk)``, ``None`` when no prefix is imported
    """
    floor = len(package_name.split("."))
    for index in range(len(parts), floor - 1, -1):
        module = sys.modules.get(".".join(parts[:index]))
        if module is not None:
            return module, parts[index:]
    return None

def imported_prefix(parts: list[str]) -> str | None:
    """The longest prefix of ``parts`` that is an imported module anywhere.

    Used only to tell "this module is imported but lives outside the commands
    package" apart from "this module was never imported", which need different
    advice.

    :param parts: the argument split on dots, exactly as typed
    :return: the dotted module name, ``None`` when no prefix is imported
    """
    for index in range(len(parts), 0, -1):
        name = ".".join(parts[:index])
        if name in sys.modules:
            return name
    return None

@CommandCaller.register
class HeatReg(CommandPackage):
    cmd = "heatReg"
    aliases = {
        "hr",
        "HR",
        "heat_reg",
        "Heat_Reg",
        "HeatReg",
        "HEAT_REG",
    }
    cmd_type = CmdTypes.CONTROL
    description = f"""
    Register an already imported class without restarting the program.

    The argument is a dotted class path inside the commands package, either
    relative to it (`control.some_file.SomeClass`) or fully qualified. The class
    is looked up in the modules that are already imported, so a module that was
    only written to disk has to be heat loaded first. Nothing is registered when
    the class is already in the registry (`enabled = False` and `heatUnload` on
    the old one first).

    Usage:
    ```
    /{cmd} <dotted.class.path>
    ```
    """
    super_permissions = True

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        tokens = persona_info.message_stripped_str.split()
        if len(tokens) != 1:
            await send_msg.send_error(
                "Expected exactly one dotted class path, "
                f"got {len(tokens)}: {persona_info.message_stripped_str!r}"
            )
            return

        raw = tokens[0]
        parts = split_module_name(raw)
        if parts is None:
            await send_msg.send_error(
                f"Invalid class path: {raw!r}. "
                "Use a dotted path inside the commands package, "
                "e.g. control.some_file.SomeClass"
            )
            return

        anchor = find_commands_anchor()
        if anchor is None:
            await send_msg.send_error(
                "Cannot locate the commands package anchor, "
                "so there is no module space to search"
            )
            return

        package_name, root = anchor
        found = find_module(package_name, absolute_parts(package_name, parts))
        if found is None:
            elsewhere = imported_prefix(parts)
            if elsewhere is not None:
                await send_msg.send_error(
                    f"{elsewhere} is imported, but it is outside the commands package "
                    f"({package_name}); only classes from there can be registered"
                )
                return
            await send_msg.send_error(
                f"Not found: no already-imported module matches {raw!r} "
                f"inside {root} ({package_name}). Load the module with heatLoad first."
            )
            return

        module, attrs = found
        target: Any = module
        for attr in attrs:
            try:
                target = getattr(target, attr)
            except AttributeError:
                await send_msg.send_error(
                    f"{module.__name__} has no attribute {'.'.join(attrs)}"
                )
                return

        if not isinstance(target, type) or not issubclass(target, CommandPackage):
            await send_msg.send_error(
                f"{raw!r} resolves to {type(target).__name__}, not a CommandPackage subclass"
            )
            return

        if target in CommandCaller.commands:
            existing = CommandCaller.commands[target]
            await send_msg.send_error(
                f"{existing.component} is already registered, "
                "unchanged; unload it with heatUnload first"
            )
            return

        if not target.enabled:
            await send_msg.send_error(
                f"{target.__module__}.{target.__qualname__} has enabled = False, "
                "so registering it would be skipped"
            )
            return

        try:
            CommandCaller.register(target)
        except TypeError as e:
            await send_msg.send_error(
                f"Cannot instantiate {target.__name__}: {e}. "
                "A class that needs constructor arguments has to be registered with "
                "register_with_args, which this command does not pass."
            )
            return
        except Exception as e:
            logger.exception(
                "Heat registration failed: {error}",
                error = str(e)
            )
            await send_msg.send_error(
                f"Registration failed: {type(e).__name__}: {e}"
            )
            return

        instance = CommandCaller.commands.get(target)
        if instance is None:
            await send_msg.send_error(
                f"{target.__module__}.{target.__qualname__} produced no registry entry"
            )
            return

        triggers = package_triggers(instance)
        await send_msg.send_prompt(
            f"Registered {instance.component}\n"
            f"triggers: {', '.join(triggers) if triggers else '(none)'}"
        )

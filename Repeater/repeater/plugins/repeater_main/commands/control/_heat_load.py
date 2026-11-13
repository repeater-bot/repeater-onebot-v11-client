import sys
import ast
import importlib
from typing import Any
from pathlib import Path
from ...assist import PersonaInfo, SendMsg
from ...cmd_info import CmdTypes
from ...command_register import(
    CommandCaller,
    CommandPackage
)
from ...logger import logger

_COMMANDS_FLAG_FILE = "_cmd_dir_flag.py"
_COMMANDS_FLAG_NAME = "commands"

def find_commands_root() -> Path | None:
    """Locate the commands directory by scanning upwards for its anchor file.

    The anchor is ``commands/_cmd_dir_flag.py`` with ``__flag__ = "commands"``,
    so nothing here depends on how many packages sit above it: the leading part
    of the dotted name is whatever the deployment happens to use.

    :return: the resolved commands directory, ``None`` when the scan finds no anchor
    """
    if __file__ is None:
        return None
    for directory in Path(__file__).resolve().parents:
        flag_file = directory / _COMMANDS_FLAG_FILE
        if flag_file.is_file() and is_commands_anchor(flag_file):
            return directory
    return None

def is_commands_anchor(flag_file: Path) -> bool:
    """Check that ``flag_file`` really declares itself as the commands anchor.

    The file is parsed instead of imported: importing it would need the dotted
    name that this very scan is trying to work out.

    :param flag_file: the candidate anchor file
    :return: whether it assigns ``__flag__ = "commands"``
    """
    try:
        tree = ast.parse(flag_file.read_text(encoding="utf-8"))
    except (OSError, SyntaxError, ValueError):
        return False
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "__flag__":
                return isinstance(node.value, ast.Constant) and node.value.value == _COMMANDS_FLAG_NAME
    return False

def commands_package_name(root: Path) -> str | None:
    """Derive the dotted name of the ``commands`` package from this module's own name.

    This module sits ``depth`` subpackages below ``root``, so dropping that many
    trailing parts off ``__name__`` leaves exactly the ``commands`` package. No
    part of the prefix is hardcoded.

    :param root: the resolved commands directory
    :return: the dotted package name, ``None`` when it cannot be derived
    """
    if __file__ is None:
        return None
    parts = __name__.split(".")
    try:
        depth = len(Path(__file__).resolve().parent.relative_to(root).parts)
    except ValueError:
        return None
    kept = len(parts) - 1 - depth
    if kept < 2:
        return None
    return ".".join(parts[:kept])

def find_commands_anchor() -> tuple[str, Path] | None:
    """The commands package name together with its directory.

    Thin wrapper over :func:`find_commands_root` + :func:`commands_package_name`
    so every heat_* command resolves the anchor the same way.

    :return: ``(package name, directory)``, ``None`` when the anchor is missing
    """
    root = find_commands_root()
    if root is None:
        return None
    package_name = commands_package_name(root)
    if package_name is None:
        return None
    return package_name, root

def split_module_name(raw: str) -> list[str] | None:
    """Split a dotted module name into its parts.

    Only dotted names are accepted: a path separator, whitespace or a drive
    letter means the caller is passing a filesystem path, and an empty part
    (``.a``, ``a.``, ``a..b``) would let ``..`` reach :func:`locate` as a
    traversal. Both are rejected here, before touching the filesystem.

    :param raw: the raw argument string
    :return: the parts of the name, ``None`` when the format is invalid
    """
    name = raw.strip()
    if not name:
        return None
    if any(sep in name for sep in ("/", "\\")):
        return None
    if any(char.isspace() for char in name):
        return None
    if ":" in name:
        return None
    parts = name.split(".")
    if any(part == "" for part in parts):
        return None
    return parts

def locate(root: Path, parts: list[str]) -> Path | None:
    """Resolve ``parts`` under ``root`` and refuse anything that lands outside.

    The boundary is checked on the resolved path, so a symlink pointing out of
    the package is rejected as well.

    :param root: the resolved ``commands`` directory
    :param parts: the parts of the module name
    :return: the resolved target path, ``None`` when it escapes ``root``
    """
    target = root.joinpath(*parts).resolve()
    if not target.is_relative_to(root):
        return None
    return target

def module_file(target: Path) -> Path | None:
    """Pick the file Python would import for ``target``.

    :param target: the resolved target path
    :return: the ``.py`` file, ``None`` when there is nothing importable there
    """
    if target.is_dir():
        init_file = target / "__init__.py"
        return init_file if init_file.is_file() else None
    candidate = target.with_name(target.name + ".py")
    return candidate if candidate.is_file() else None

def display_trigger(package: type[CommandPackage[Any]]) -> str:
    """A printable name for a registered package.

    ``cmd`` is either a string or a tuple of triggers, and a package whose
    import succeeded must not make the report itself blow up on the tuple form.

    :param package: the registered package class
    :return: the trigger, or the class name when there is no plain string one
    """
    trigger = getattr(package, "cmd", None)
    if isinstance(trigger, tuple):
        return str(trigger[0]) if trigger else package.__name__
    if isinstance(trigger, str) and trigger:
        return trigger
    return package.__name__

@CommandCaller.register
class HeatLoad(CommandPackage):
    cmd = "heatLoad"
    aliases = {
        "hl",
        "HL",
        "heat_load",
        "Heat_Load",
        "HeatLoad",
        "HEAT_LOAD",
    }
    cmd_type = CmdTypes.CONTROL
    description = f"""
    Load a new file without restarting the program.

    The argument is the dotted module name relative to the commands package,
    e.g. `control.some_new_command` for `commands/control/some_new_command.py`.
    Paths and anything resolving outside the commands package are refused, and
    so is any module already imported in this process: reloading it would leak
    the previous matchers, restart the program instead.

    Usage: 
    ```
    /{cmd} <dotted.module.name>
    ```
    """
    super_permissions = True

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        raw = persona_info.message_stripped_str

        parts = split_module_name(raw)
        if parts is None:
            await send_msg.send_error(
                f"Invalid module name: {raw!r}. "
                "Use a dotted name relative to the commands package, "
                "e.g. control.some_new_command"
            )
            return

        anchor = find_commands_anchor()
        if anchor is None:
            await send_msg.send_error(
                f"Cannot locate the commands directory: no {_COMMANDS_FLAG_FILE} declaring "
                f'__flag__ = "{_COMMANDS_FLAG_NAME}" found above {Path(__file__).resolve().parent}, '
                f"or the package name cannot be derived from {__name__}"
            )
            return

        package_name, root = anchor

        target = locate(root, parts)
        if target is None:
            await send_msg.send_error(
                f"Refused: {raw!r} resolves outside the commands package ({root})"
            )
            return

        target_file = module_file(target)
        if target_file is None:
            await send_msg.send_error(
                f"Not found: no importable module at {raw!r} "
                f"({target.relative_to(root).as_posix()} is neither a .py file "
                "nor a package directory)"
            )
            return

        dotted = f"{package_name}.{'.'.join(parts)}"
        if dotted in sys.modules:
            await send_msg.send_error(
                f"Already loaded: {dotted} is already imported in this process. "
                "Reloading it would leak the previous matchers, restart the program instead."
            )
            return

        registered_before = set(CommandCaller.commands)
        try:
            importlib.invalidate_caches()
            importlib.import_module(dotted)
        except Exception as e:
            logger.exception(
                "Heat loading failed: {error}",
                error = str(e)
            )
            await send_msg.send_error(
                f"Import failed: {type(e).__name__}: {e}"
            )
            return

        registered = sorted(
            display_trigger(package)
            for package in CommandCaller.commands
            if package not in registered_before
        )
        registered_text = ", ".join(registered) if registered else "(none)"

        await send_msg.send_prompt(
            f"Loaded {'.'.join(parts)}\n"
            f"file: {target_file.relative_to(root).as_posix()}\n"
            f"module: {dotted}\n"
            f"registered: {registered_text}"
        )

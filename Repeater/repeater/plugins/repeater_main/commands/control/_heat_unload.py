import uuid
from typing import Any
from ...assist import PersonaInfo, SendMsg
from ...cmd_info import CmdTypes
from ...command_register import(
    CommandCaller,
    CommandPackage
)
from ...logger import logger

def resolve_package(raw: str) -> type[CommandPackage[Any]] | None:
    """Resolve a trigger or a component to its registered package.

    Components are looked up first (that is also the order
    :meth:`CommandCaller.match_trigger_or_component` uses), then bare triggers,
    then triggers with a command prefix still attached so that a pasted
    ``/trigger`` resolves as well.

    :param raw: the argument as typed, already stripped
    :return: the package class, ``None`` when nothing matches
    """
    try:
        return CommandCaller.match_component(raw)
    except KeyError:
        pass

    try:
        return CommandCaller.match_trigger(raw)
    except KeyError:
        pass

    for prefix in CommandCaller.cmd_prefixs():
        if not raw.startswith(prefix):
            continue
        try:
            return CommandCaller.match_trigger(raw.removeprefix(prefix))
        except KeyError:
            continue
    return None

async def call_chain(task_id: uuid.UUID) -> set[uuid.UUID]:
    """The ancestors of ``task_id`` in the horizontal call chain.

    Cancelling one of those would pull the rug out from under the request that
    is asking for the unload, so they are collected first and left alone.

    :param task_id: the id of the task running this command
    :return: the ids of its ancestors
    """
    chain: set[uuid.UUID] = set()
    async with CommandCaller.call_index_lock:
        parent = CommandCaller.reverse_call_index.get(task_id)
        while parent is not None and parent not in chain:
            chain.add(parent)
            parent = CommandCaller.reverse_call_index.get(parent)
    return chain

async def cancel_running(
    package: type[CommandPackage[Any]],
    protected: set[uuid.UUID]
) -> tuple[list[uuid.UUID], list[uuid.UUID]]:
    """Cancel the package's running tasks.

    Only cancel: ``run_handle`` pops the task out of ``runnings``,
    ``running_map`` and ``running_packages`` in its own ``finally`` once the
    cancellation lands, so there is nothing to scrub here.

    :param package: the package class to unload
    :param protected: task ids that must not be cancelled
    :return: ``(cancelled, skipped)`` task ids
    """
    cancelled: list[uuid.UUID] = []
    skipped: list[uuid.UUID] = []

    for task_id in await CommandCaller.all_this_running(package):
        if task_id in protected:
            skipped.append(task_id)
            continue
        running = await CommandCaller.get_global_running(task_id)
        if running is None:
            continue
        running.cancel()
        cancelled.append(task_id)

    return cancelled, skipped

def package_triggers(instance: CommandPackage[Any]) -> list[str]:
    """The triggers a package answers to, for the report.

    Takes the package *instance*, not the class: ``get_package_aliases`` reads
    ``component`` when ``loading.component_is_trigger`` is on (it is on by
    default), and ``component`` is an instance property.

    :param instance: the registered package instance
    :return: the main trigger(s) followed by the aliases
    """
    triggers: list[str] = []
    cmd = getattr(instance, "cmd", None)
    if isinstance(cmd, tuple):
        triggers.extend(str(item) for item in cmd)
    elif isinstance(cmd, str) and cmd:
        triggers.append(cmd)
    for alias in sorted(CommandCaller.get_package_aliases(instance), key = str):
        text = str(alias)
        if text not in triggers:
            triggers.append(text)
    return triggers

@CommandCaller.register
class HeatUnload(CommandPackage):
    cmd = "heatUnload"
    aliases = {
        "hu",
        "HU",
        "heat_unload",
        "Heat_Unload",
        "HeatUnload",
        "HEAT_UNLOAD",
    }
    cmd_type = CmdTypes.CONTROL
    description = f"""
    Remove a command from the registry without restarting the program.

    The argument is either a trigger (`{cmd}`-style name or any alias, with or
    without the command prefix) or a component (`Repeater.CONTROL.SomeCommand`).
    Its running tasks are cancelled first, then the command itself goes away:
    matcher plus every registry index entry, while the module stays imported,
    so restart the program to get the command back.

    Usage:
    ```
    /{cmd} <trigger | component>
    ```
    """
    super_permissions = True

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        tokens = persona_info.message_stripped_str.split()
        if len(tokens) != 1:
            await send_msg.send_error(
                "Expected exactly one trigger or component, "
                f"got {len(tokens)}: {persona_info.message_stripped_str!r}"
            )
            return

        raw = tokens[0]
        package = resolve_package(raw)
        if package is None:
            await send_msg.send_error(f"No registered command matches {raw!r}")
            return

        if package is type(self):
            await send_msg.send_error(
                "Refusing to unload the command that is handling this request"
            )
            return

        try:
            registered = CommandCaller.get_instance(package)
        except KeyError:
            await send_msg.send_error(f"Command instance of {raw!r} not found")
            return

        component = registered.component
        triggers = package_triggers(registered)

        try:
            current_task_id = await CommandCaller.get_task_id()
        except RuntimeError:
            current_task_id = None
        protected = await call_chain(current_task_id) if current_task_id is not None else set()

        cancelled, skipped = await cancel_running(package, protected)

        try:
            await CommandCaller.adestroy(package)
        except Exception as e:
            logger.exception(
                "Heat unloading failed: {error}",
                error = str(e)
            )
            await send_msg.send_error(
                f"Cancelled {len(cancelled)} running task(s) and removed "
                f"{component} from the registry, "
                f"but on_adestroy raised {type(e).__name__}: {e}"
            )
            return

        lines = [
            f"Unloaded {component}",
            f"triggers: {', '.join(triggers) if triggers else '(none)'}",
        ]
        if cancelled:
            lines.append(f"cancelled: {len(cancelled)} running task(s)")
            lines.extend(f"- [{task_id}]" for task_id in cancelled)
        if skipped:
            lines.append(
                f"skipped: {len(skipped)} task(s) in the current call chain "
                f"({', '.join(str(task_id) for task_id in skipped)})"
            )
        await send_msg.send_prompt("\n".join(lines))

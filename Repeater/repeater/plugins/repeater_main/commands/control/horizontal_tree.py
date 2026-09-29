import uuid
import asyncio
from ...assist import PersonaInfo, SendMsg, Namespace
from ...cmd_info import CmdTypes
from ...command_register import(
    CommandCaller,
    CommandPackage,
    RunningPackage
)

@CommandCaller.register
class HorizontalTree(CommandPackage):
    cmd = "horizontalTree"
    aliases = {
        "ht",
        "HT",
        "horizontal_tree",
        "Horizontal_Tree",
        "HorizontalTree",
        "HORIZONTAL_TREE"
    }
    cmd_type = CmdTypes.CONTROL
    description = f"""
    Shows the child call tree for the specified task.

    Usage: 
    ```
    /{cmd} task_id
    ```
    """
    
    @staticmethod
    async def forward_index_snapshot() -> dict[uuid.UUID, set[RunningPackage]]:
        async with CommandCaller.call_index_lock:
            async with CommandCaller.running_lock:
                return {
                    k: {CommandCaller.runnings[id] for id in v}
                    for k, v in CommandCaller.forward_call_index.items()
                }

    @staticmethod
    async def reverse_index_snapshot() -> dict[uuid.UUID, uuid.UUID]:
        async with CommandCaller.call_index_lock:
            return {k: v for k, v in CommandCaller.reverse_call_index.items()}

    @staticmethod
    def find_root(reverse: dict[uuid.UUID, uuid.UUID], task_id: uuid.UUID) -> uuid.UUID:
        root_task_id = task_id

        while True:
            now_task_id = reverse.get(root_task_id)
            if now_task_id is None:
                break
            root_task_id = now_task_id

        return root_task_id

    @staticmethod
    def render_tree(forward: dict[uuid.UUID, set[RunningPackage]], root: RunningPackage) -> str:
        lines: list[str] = [
            f"[{root.task_id}]({root.package.component})"
        ]

        stack: list[tuple[RunningPackage, str, bool]] = []
        children = sorted(forward.get(root.task_id, ()), key=lambda x: x.start_monotonic_time)
        for i in range(len(children) - 1, -1, -1):
            stack.append((children[i], "", i == len(children) - 1))

        while stack:
            node, prefix, is_last = stack.pop()
            lines.append(f"{prefix}{'└ ' if is_last else '├ '}[{node.task_id}]({node.package.component})")

            child_prefix = prefix + ("  " if is_last else "│ ")
            children = sorted(forward.get(node.task_id, ()), key=lambda x: x.start_monotonic_time)
            for i in range(len(children) - 1, -1, -1):
                stack.append((children[i], child_prefix, i == len(children) - 1))

        return "\n".join(lines)

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        task_id_str = persona_info.message_stripped_str

        if task_id_str:
            try:
                task_id = uuid.UUID(task_id_str)
            except ValueError:
                await send_msg.send_error(f"Invalid task ID: {task_id_str}")
                return

            now_user_running = await CommandCaller.get_running_ids(persona_info.namespace)

            if task_id not in now_user_running:
                await send_msg.send_error(f"Task ID {task_id} is not running")
                return
        else:
            reverse_snapshot = await self.reverse_index_snapshot()
            now_task_id = reverse_snapshot.get(persona_info.task_id)

            if now_task_id is None:
                await send_msg.send_error(f"Unable to reverse query the root from the current node.")
                return

            task_id = await asyncio.to_thread(
                self.find_root,
                reverse_snapshot,
                now_task_id,
            )

        snapshot = await self.forward_index_snapshot()

        root_node = await CommandCaller.get_running(persona_info.namespace, task_id)

        if root_node is None:
            await send_msg.send_error("A valid root node could not be traced.")
            return

        result = await asyncio.to_thread(
            self.render_tree,
            snapshot,
            root_node,
        )

        await send_msg.send_check_length_prompt(
            result,
            code_block = True
        )
from httpx import HTTPStatusError
from ...command_register import(
    CommandCaller,
    CommandPackage
)
from ...cmd_info import CmdTypes
from ...assist import PersonaInfo, SendMsg
from ...clients import AlivedClient

@CommandCaller.register
class Alived(CommandPackage):
    cmd = "alived"
    aliases = {
        "alv",
        "ALV",
        "Alived",
        "ALIVED",
    }
    cmd_type = CmdTypes.ALIVED
    description = f"""
    Check the online status of all backends.

    Usage:
    ```
    /{cmd}
    ```
    or
    ```
    /{cmd} backend_name
    ```
    """
    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        user_configs = await persona_info.get_user_configs()
        client = AlivedClient(persona_info, user_configs)

        backend_name = persona_info.message_stripped_str
        if backend_name:
            alived_time = await client.alived_time(backend_name)
            await send_msg.send_text(
                f"[{backend_name}]: Online\nAlived time: {alived_time / 1e9:.3f}s"
            )
        else:
            alive_times = await client.alived_times()
            text_buffer: list[str] = []
            for backend_name, alived_time in alive_times.items():
                text_buffer.append(
                    f"[{backend_name}]: Online\nAlived time: {alived_time / 1e9:.3f}s"
                )
            await send_msg.send_text("\n".join(text_buffer))
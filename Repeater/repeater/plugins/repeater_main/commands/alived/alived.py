import httpx
from ...command_register import(
    CommandCaller,
    CommandPackage
)
from ...cmd_info import CmdTypes
from ...assist import PersonaInfo, SendMsg, format_time_duration_ns
from ...clients import AlivedClient
from ...client_configs import storage_configs

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
            try:
                await send_msg.send_text(
                    f"[{backend_name}]: Online\nAlived time: {format_time_duration_ns(alived_time, use_abbreviation = True)}"
                )
            except httpx.ConnectError as e:
                await send_msg.send_text(f"[{backend_name}]: Offline")

        else:
            backends = storage_configs.backends.keys()
            text_buffer: list[str] = []
            for backend_name in backends:
                try:
                    alived_time = await client.alived_time(backend_name)
                    text_buffer.append(
                        f"[{backend_name}]: Online\nAlived time: {format_time_duration_ns(alived_time, use_abbreviation = True)}"
                    )
                except httpx.ConnectError as e:
                    text_buffer.append(f"[{backend_name}]: Offline")

            text = "\n\n".join(text_buffer)
            try:
                await send_msg.send_render(text)
            except httpx.ConnectError as e:
                await send_msg.send_text(text)


from ...assist import PersonaInfo, SendMsg
from ...cmd_info import CmdTypes
from ...command_register import(
    CommandCaller,
    CommandPackage
)
from ...clients import ModelInfoClient, ModelInfo

@CommandCaller.register
class PingProviderHost(CommandPackage):
    cmd = "pingProviderHost"
    aliases = {
        "pph",
        "PPH",
        "ping_provider_host",
        "Ping_Provider_Host",
        "PingProviderHost",
        "PING_PROVIDER_HOST",
    }
    description = f"""
    Initiates a ping request to the specified vendor host,
    if this feature is required for normal use on a Linux-based server,
    the server needs to be upgraded.

    Usage:
    ```
    /{cmd} [model_id]
    ```
    """
    cmd_type = CmdTypes.MODEL

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        user_configs = await persona_info.get_user_configs()
        model_info_client = ModelInfoClient(persona_info, user_configs)
        model_id = persona_info.message_stripped_str
        if not model_id:
            model_id = None

        response = await model_info_client.ping_provider(
            persona_info.namespace_str,
            model_id = model_id
        )
        if response:
            ping_response = response.get_data()
            if ping_response is None:
                await send_msg.send_error("Error: No Model Data")
            else:
                text_buffer: list[str] = []
                text_buffer.append(f"Successful Times: {ping_response.success_count}")
                text_buffer.append(f"Average Time Spent: {ping_response.average_time_spent}")
                for detail in ping_response.details:
                    statistics = detail.to_statistics()
                    text_buffer.append("")
                    text_buffer.append(f"**Host** [{detail.ip}]:")
                    text_buffer.append(f"**names:**")
                    for name in detail.host_names:
                        text_buffer.append(f"  - `{name}`")
                    text_buffer.append(f"**times:**")
                    for time in detail.time:
                        text_buffer.append(f"  - {time:.4f}ms")
                    text_buffer.append(f"**packet loss:** {detail.packet_loss:.2%}")
                    text_buffer.append(f"**max time:** {statistics.max:.4f}ms")
                    text_buffer.append(f"**min time:** {statistics.min:.4f}ms")
                    text_buffer.append(f"**avg time:** {statistics.mean:.4f}ms")
                    text_buffer.append(f"**median time:** {statistics.median:.4f}ms")
                    text_buffer.append(f"**standard deviation:** {statistics.std:.4f}ms")
                    text_buffer.append(f"**variance:** {statistics.var:.4f}ms")
                    text_buffer.append(f"**coefficient of variation:** {statistics.cv:.2%}")
                await send_msg.send_render_prompt("\n".join(text_buffer))
        else:
            await send_msg.send_response_check_code(response)
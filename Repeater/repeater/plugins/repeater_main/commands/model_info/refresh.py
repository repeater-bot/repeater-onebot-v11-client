from ...assist import PersonaInfo, SendMsg
from ...cmd_info import CmdTypes
from ...command_register import(
    CommandCaller,
    CommandPackage
)
from ...clients import ModelInfoClient, ModelInfo

@CommandCaller.register
class RefreshModels(CommandPackage):
    cmd = "refreshModels"
    aliases = {
        "rm",
        "RM",
        "refresh_models",
        "Refresh_Models",
        "RefreshModels",
        "REFRESH_MODELS",
    }
    description = f"""
    Refresh the model pool.

    Usage:
    ```
    /{cmd}
    /{cmd} provider_id
    ```
    """
    cmd_type = CmdTypes.MODEL

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        user_configs = await persona_info.get_user_configs()
        model_info_client = ModelInfoClient(persona_info, user_configs)
        provider_id = persona_info.message_stripped_str

        if not provider_id:
            provider_id = None

        response = await model_info_client.refresh(provider_id)

        if response:
            data = response.get_data()
            if data is None:
                await send_msg.send_error("Invalid response data.")
                send_msg.break_handler()
            
            await send_msg.send_response(
                response,
                message = data.message
            )
        else:
            await send_msg.send_error_render(response)
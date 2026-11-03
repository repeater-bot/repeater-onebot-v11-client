from ....assist import PersonaInfo, SendMsg
from ....cmd_info import CmdTypes
from ....command_register import(
    CommandCaller,
    CommandPackage
)
from ....clients import ContextClient


@CommandCaller.register
class GetContextTotalLength(CommandPackage):
    cmd = "getContextTotalLength"
    aliases = {
        "gctl",
        "GCTL",
        "get_context_total_length",
        "Get_Context_Total_Length",
        "GetContextTotalLength",
        "GET_CONTEXT_TOTAL_LENGTH",
    }
    cmd_type = CmdTypes.CONTEXT

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        user_config = await persona_info.get_user_configs()
        context_client = ContextClient(persona_info, user_config)
        response = await context_client.get_context_total_length()

        if response:
            data = response.get_data()
            if data is None:
                await send_msg.send_error("Unable to process data.")
            else:
                await send_msg.send_prompt(
                    f"length: {data.context_length}\n"
                    f"total_text_length: {data.total_context_length}\n"
                    f"average_content_length: {data.average_content_length}\n"
                )
        else:
            await send_msg.send_response_check_code(response, "Get Context Total Length Failed")
from ....assist import PersonaInfo, SendMsg
from ....cmd_info import CmdTypes
from ....command_register import(
    CommandCaller,
    CommandPackage
)
from ....clients import ContextClient


@CommandCaller.register
class GetLastContent(CommandPackage):
    cmd = "getLastContent"
    aliases = {
        "glc",
        "GLC",
        "get_last_content",
        "Get_Last_Content",
        "GetLastContent",
        "GET_LAST_CONTENT",
    }
    cmd_type = CmdTypes.CONTEXT

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        user_config = await persona_info.get_user_configs()
        context_client = ContextClient(persona_info, user_config)

        response = await context_client.get_context()
        if response:
            context = response.get_data()
            if context is None:
                await send_msg.send_error("Error: No Context Data")
            elif len(context) > 0:
                last_content = context[-1]
                await send_msg.send_chat_response(
                    last_content.reasoning_content,
                    last_content.content
                )
            else:
                await send_msg.send_error("Error: Context Data is Empty")
        else:
            await send_msg.send_response_check_code(response)
from ....assist import PersonaInfo, SendMsg
from ....cmd_info import CmdTypes
from ....command_register import(
    CommandCaller,
    CommandPackage
)
from ....clients import ContextClient


@CommandCaller.register
class CheckRoleStructure(CommandPackage):
    cmd = "checkRoleStructure"
    aliases = {
        "crs",
        "CRS",
        "check_role_structure",
        "Check_Role_Structure",
        "CheckRoleStructure",
        "CHECK_ROLE_STRUCTURE",
    }
    cmd_type = CmdTypes.CONTEXT

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        user_config = await persona_info.get_user_configs()
        context_client = ContextClient(persona_info, user_config)
        response = await context_client.check_role_structure()

        if response.code == 200:
            data = response.get_data()
            if data is not None:
                await send_msg.send_prompt(data.message)
            else:
                await send_msg.send_prompt("Check Role Structure Data is Invalid")
        else:
            await send_msg.send_response_check_code(response, "Check Role Structure Failed")
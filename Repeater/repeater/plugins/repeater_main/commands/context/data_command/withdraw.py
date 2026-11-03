from ....assist import PersonaInfo, SendMsg
from ....cmd_info import CmdTypes
from ....command_register import(
    CommandCaller,
    CommandPackage
)
from ....clients import ContextClient


@CommandCaller.register
class Withdraw(CommandPackage):
    cmd = "withdraw"
    aliases = {
        "w",
        "W",
        "Withdraw",
        "WITHDRAW",
    }
    cmd_type = CmdTypes.CONTEXT

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        user_config = await persona_info.get_user_configs()
        context_client = ContextClient(persona_info, user_config)
        if persona_info.args_str:
            try:
                num = int(persona_info.args_str)
            except ValueError:
                await send_msg.send_error("Please input a valid number")
                return

            if num < 1:
                await send_msg.send_error("Please input a number greater than 0")
                return
        else:
            num = 1

        response = await context_client.withdraw(num)

        if response:
            data = response.get_data()
            if data is None:
                await send_msg.send_error("Unable to process data.")
                return
            await send_msg.send_prompt(
                f"Deleted: {data.deleted}\n"
                f"Remaining: {len(data.context)}\n"
            )
        else:
            await send_msg.send_response_check_code(response, "Withdraw Failed")
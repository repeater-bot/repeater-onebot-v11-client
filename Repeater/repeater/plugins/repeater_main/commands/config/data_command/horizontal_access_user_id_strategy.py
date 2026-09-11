from ....assist import PersonaInfo, SendMsg, Response
from ....cmd_info import CmdTypes
from ....command_register import CommandCaller
from ..._bases import BaseConfig


@CommandCaller.register
class HorizontalAccessUserIDStrategy(BaseConfig):
    cmd = "horizontalAccessUserIDStrategy"
    aliases = {
        "hauids",
        "HAUIDS",
        "horizontal_access_user_id_strategy",
        "Horizontal_Access_User_ID_Strategy",
        "HorizontalAccessUserIDStrategy",
        "HORIZONTAL_ACCESS_USER_ID_STRATEGY",
    }
    field = "horizontal_access_user_id_strategy"
    description = f"""
    How the back end should commit the user when it accesses another instance horizontally.
    Possible values:
      - local_instance: Only the native user is passed, which has the effect of using the global default space.
      - separate: Passing both the instance and the user ID has the effect of isolating everyone. This is the default.
      - users: Passing only the user ID has the effect of sharing memory with the user, but can cause data corruption.

    Usage:
      /{cmd} strategy
    """

    # 字符串类型，不需要重写 parse_value
    
    async def finish_message(
            self,
            persona_info: PersonaInfo,
            send_msg: SendMsg,
            response: Response,
            field: str,
            value: str
        ):
        await send_msg.send_response_check_code(response, f"Set Horizontal_Access_User_ID_Strategy to {value}")
from ....cmd_info import CmdTypes
from ....command_register import CommandCaller
from ..._bases import GetActiveBranch, UserdataCmdsType


@CommandCaller.register
class GetPromptActiveBranch(GetActiveBranch):
    cmd = "getPromptActiveBranch"
    aliases = {
        "gpab",
        "GPAB",
        "get_prompt_active_branch",
        "Get_Prompt_Active_Branch",
        "GetPromptActiveBranch",
        "GET_PROMPT_ACTIVE_BRANCH",
    }
    cmd_type = CmdTypes.BRANCH_PROMPT
    userdata_cmds_type: UserdataCmdsType = UserdataCmdsType.PROMPT
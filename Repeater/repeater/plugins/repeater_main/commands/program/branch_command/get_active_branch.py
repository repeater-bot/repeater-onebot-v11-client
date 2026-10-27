from ....cmd_info import CmdTypes
from ....command_register import CommandCaller
from ..._bases import GetActiveBranch, UserdataCmdsType


@CommandCaller.register
class GetProgramBranchsList(GetActiveBranch):
    cmd = "getProgramActiveBranch"
    aliases = {
        "gpgmbl",
        "GPGMBL",
        "get_program_active_branch",
        "Get_Program_Active_Branch",
        "GetProgramActiveBranch",
        "GET_PROMPT_ACTIVE_BRANCH",
    }
    cmd_type = CmdTypes.BRANCH_PROMPT
    userdata_cmds_type: UserdataCmdsType = UserdataCmdsType.PROMPT
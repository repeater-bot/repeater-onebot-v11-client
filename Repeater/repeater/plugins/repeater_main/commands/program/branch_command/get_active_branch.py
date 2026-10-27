from ....cmd_info import CmdTypes
from ....command_register import CommandCaller
from ..._bases import GetActiveBranch, UserdataCmdsType


@CommandCaller.register
class GetProgramActiveBranch(GetActiveBranch):
    cmd = "getProgramActiveBranch"
    aliases = {
        "gpgmab",
        "GPGMAB",
        "get_program_active_branch",
        "Get_Program_Active_Branch",
        "GetProgramActiveBranch",
        "GET_PROGRAM_ACTIVE_BRANCH",
    }
    cmd_type = CmdTypes.BRANCH_PROGRAM
    userdata_cmds_type: UserdataCmdsType = UserdataCmdsType.PROGRAM
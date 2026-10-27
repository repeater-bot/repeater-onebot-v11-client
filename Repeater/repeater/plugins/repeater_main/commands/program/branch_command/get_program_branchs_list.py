from ....cmd_info import CmdTypes
from ....command_register import CommandCaller
from ..._bases import GetBranchList, UserdataCmdsType


@CommandCaller.register
class GetProgramBranchsList(GetBranchList):
    cmd = "getProgramBranchList"
    aliases = {
        "gpgmbl",
        "GPGMBL",
        "get_program_branchs_list",
        "Get_Program_Branchs_List",
        "GetProgramBranchsList",
        "GET_PROMPT_BRANCHS_LIST",
    }
    cmd_type = CmdTypes.BRANCH_PROMPT
    userdata_cmds_type: UserdataCmdsType = UserdataCmdsType.PROMPT
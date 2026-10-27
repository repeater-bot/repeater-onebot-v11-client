from ....cmd_info import CmdTypes
from ....command_register import CommandCaller
from ..._bases import GetBranchList, UserdataCmdsType


@CommandCaller.register
class GetContextBranchsList(GetBranchList):
    cmd = "getContextBranchsList"
    aliases = {
        "gcbl",
        "GCBL",
        "get_context_branchs_list",
        "Get_Context_Branchs_List",
        "GetContextBranchsList",
        "GET_CONTEXT_BRANCHS_LIST",
    }
    cmd_type = CmdTypes.BRANCH_CONTEXT
    userdata_cmds_type: UserdataCmdsType = UserdataCmdsType.CONTEXT
from ....cmd_info import CmdTypes
from ....command_register import CommandCaller
from ..._bases import GetActiveBranch, UserdataCmdsType


@CommandCaller.register
class GetContextActiveBranch(GetActiveBranch):
    cmd = "getContextActiveBranch"
    aliases = {
        "gcab",
        "GCAB",
        "get_context_active_branch",
        "Get_Context_Active_Branch",
        "GetContextActiveBranch",
        "GET_CONTEXT_ACTIVE_BRANCH",
    }
    cmd_type = CmdTypes.BRANCH_CONTEXT
    userdata_cmds_type: UserdataCmdsType = UserdataCmdsType.CONTEXT
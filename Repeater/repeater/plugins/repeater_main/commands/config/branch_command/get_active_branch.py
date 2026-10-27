from ....cmd_info import CmdTypes
from ....command_register import CommandCaller
from ..._bases import GetActiveBranch, UserdataCmdsType


@CommandCaller.register
class GetConfigActiveBranch(GetActiveBranch):
    cmd = "getConfigActiveBranch"
    aliases = {
        "gcfgab",
        "GCFGAB",
        "get_config_active_branch",
        "Get_Config_Active_Branch",
        "GetConfigActiveBranch",
        "GET_CONFIG_ACTIVE_BRANCH",
    }
    cmd_type = CmdTypes.BRANCH_CONFIG
    userdata_cmds_type: UserdataCmdsType = UserdataCmdsType.CONFIG
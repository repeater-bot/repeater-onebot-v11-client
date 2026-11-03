from ....cmd_info import CmdTypes
from ....command_register import CommandCaller
from ..._bases import DeleteBranch, UserdataCmdsType

@CommandCaller.register
class DeleteConfig(DeleteBranch):
    cmd = "deleteConfig"
    aliases = {
        "dcfg",
        "DCFG",
        "delete_config",
        "Delete_Config",
        "DeleteConfig",
        "DELETE_CONFIG",
    }
    cmd_type = CmdTypes.BRANCH_CONFIG
    userdata_cmds_type: UserdataCmdsType = UserdataCmdsType.CONFIG
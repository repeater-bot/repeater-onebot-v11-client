from ....cmd_info import CmdTypes
from ....command_register import CommandCaller
from ..._bases import DeleteBranch, UserdataCmdsType


@CommandCaller.register
class DeleteProgram(DeleteBranch):
    cmd = "deleteProgram"
    aliases = {
        "dpgm",
        "DPGM",
        "delete_program",
        "Delete_Program",
        "DeleteProgram",
        "DELETE_PROGRAM",
    }
    cmd_type = CmdTypes.BRANCH_PROGRAM
    userdata_cmds_type: UserdataCmdsType = UserdataCmdsType.PROGRAM
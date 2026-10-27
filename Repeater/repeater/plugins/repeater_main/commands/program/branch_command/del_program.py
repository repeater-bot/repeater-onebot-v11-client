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
        "DELETE_PROMPT",
    }
    cmd_type = CmdTypes.BRANCH_PROMPT
    userdata_cmds_type: UserdataCmdsType = UserdataCmdsType.PROMPT
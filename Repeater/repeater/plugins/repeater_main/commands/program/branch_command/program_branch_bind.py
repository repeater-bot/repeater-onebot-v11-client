from ....cmd_info import CmdTypes
from ....command_register import CommandCaller
from ..._bases import BindBranch, UserdataCmdsType


@CommandCaller.register
class ProgramBranchBind(BindBranch):
    cmd = "programBranchBind"
    aliases = {
        "pgmbb",
        "PGMBB",
        "program_branch_bind",
        "Program_Branch_Bind",
        "ProgramBranchBind",
        "PROGRAM_BRANCH_BIND",
    }
    cmd_type = CmdTypes.BRANCH_PROGRAM
    userdata_cmds_type: UserdataCmdsType = UserdataCmdsType.PROGRAM
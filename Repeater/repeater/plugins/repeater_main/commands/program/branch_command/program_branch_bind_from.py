from ....cmd_info import CmdTypes
from ....command_register import CommandCaller
from ..._bases import BindBranchFrom, UserdataCmdsType


@CommandCaller.register
class ProgramBranchBindFrom(BindBranchFrom):
    cmd = "programBranchBindFrom"
    aliases = {
        "pgmbbf",
        "PGMBBF",
        "program_branch_bind_from",
        "Program_Branch_Bind_From",
        "ProgramBranchBindFrom",
        "PROGRAM_BRANCH_BIND_FROM",
    }
    cmd_type = CmdTypes.BRANCH_PROGRAM
    userdata_cmds_type: UserdataCmdsType = UserdataCmdsType.PROGRAM
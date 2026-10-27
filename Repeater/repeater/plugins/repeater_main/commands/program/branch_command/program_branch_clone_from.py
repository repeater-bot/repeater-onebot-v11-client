from ....cmd_info import CmdTypes
from ....command_register import CommandCaller
from ..._bases import CloneBranchFrom, UserdataCmdsType


@CommandCaller.register
class ProgramBranchCloneFrom(CloneBranchFrom):
    cmd = "programBranchCloneFrom"
    aliases = {
        "pgmbcf",
        "PGMBCF",
        "program_branch_clone_from",
        "Program_Branch_Clone_From",
        "ProgramBranchCloneFrom",
        "PROGRAM_BRANCH_CLONE_FROM",
    }
    cmd_type = CmdTypes.BRANCH_PROGRAM
    userdata_cmds_type: UserdataCmdsType = UserdataCmdsType.PROGRAM
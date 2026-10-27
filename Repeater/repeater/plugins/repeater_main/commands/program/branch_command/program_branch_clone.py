from ....cmd_info import CmdTypes
from ....command_register import CommandCaller
from ..._bases import CloneBranch, UserdataCmdsType


@CommandCaller.register
class ProgramBranchClone(CloneBranch):
    cmd = "programBranchClone"
    aliases = {
        "pgmbc",
        "PGMBC",
        "program_branch_clone",
        "Program_Branch_Clone",
        "ProgramBranchClone",
        "PROMPT_BRANCH_CLONE",
    }
    cmd_type = CmdTypes.BRANCH_PROMPT
    userdata_cmds_type: UserdataCmdsType = UserdataCmdsType.PROMPT
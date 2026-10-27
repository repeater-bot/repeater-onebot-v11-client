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
        "PROMPT_BRANCH_BIND",
    }
    cmd_type = CmdTypes.BRANCH_PROMPT
    userdata_cmds_type: UserdataCmdsType = UserdataCmdsType.PROMPT
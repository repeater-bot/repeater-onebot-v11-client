from ....cmd_info import CmdTypes
from ....command_register import CommandCaller
from ..._bases import BranchInfo, UserdataCmdsType


@CommandCaller.register
class ProgramBranchInfo(BranchInfo):
    cmd = "programBranchInfo"
    aliases = {
        "pgmbi",
        "PGMBI",
        "program_branch_info",
        "Program_Branch_Info",
        "ProgramBranchInfo",
        "PROMPT_BRANCH_INFO",
    }
    cmd_type = CmdTypes.BRANCH_PROMPT
    userdata_cmds_type: UserdataCmdsType = UserdataCmdsType.PROMPT
from ....cmd_info import CmdTypes
from ....command_register import CommandCaller
from ..._bases import ChangeBranch, UserdataCmdsType


@CommandCaller.register
class ChangeProgramBranch(ChangeBranch):
    cmd = "changeProgramBranch"
    aliases = {
        "cpgmb",
        "CPGMB",
        "change_program_branch",
        "Change_Program_Branch",
        "ChangeProgramBranch",
        "CHANGE_PROMPT_BRANCH",
    }
    cmd_type = CmdTypes.BRANCH_PROMPT
    userdata_cmds_type: UserdataCmdsType = UserdataCmdsType.PROMPT
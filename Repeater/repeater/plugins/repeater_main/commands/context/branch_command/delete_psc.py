from ....assist import PersonaInfo
from ....cmd_info import CmdTypes
from ....command_register import CommandCaller
from ..._bases import DeleteBranch, UserdataCmdsType


@CommandCaller.register
class DeletePublicSpaceContext(DeleteBranch):
    cmd = "deletePublicSpaceContext"
    aliases = {
        "dpsc",
        "DPSC",
        "delete_public_space_context",
        "Delete_Public_Space_Context",
        "DeletePublicSpaceContext",
        "DELETE_PUBLIC_SPACE_CONTEXT",
    }
    cmd_type = CmdTypes.BRANCH_CONTEXT
    userdata_cmds_type: UserdataCmdsType = UserdataCmdsType.CONTEXT

    async def get_namespace(self, persona_info: PersonaInfo) -> str:
        return persona_info.public_namespace_str
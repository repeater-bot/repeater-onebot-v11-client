from abc import abstractmethod

from ....clients import (
    ContextClient,
    PromptClient,
    ConfigClient,
    ProgramDataClient,
    UserDataClient
)
from ....assist import PersonaInfo, SendMsg, Namespace
from ....cmd_info import CmdTypes
from ....command_register import CommandPackage
from ..userdata_cmds_type import UserdataCmdsType

class BaseBranch(CommandPackage):
    cmd_type = CmdTypes.BRANCH
    userdata_cmds_type: UserdataCmdsType = UserdataCmdsType.NONE

    async def get_namespace(self, persona_info: PersonaInfo) -> str | Namespace | None:
        pass
    
    async def get_client(self, persona_info: PersonaInfo) -> UserDataClient:
        user_configs = await persona_info.get_user_configs()
        match self.userdata_cmds_type:
            case UserdataCmdsType.CONTEXT:
                return ContextClient(
                    persona_info,
                    user_configs,
                    await self.get_namespace(persona_info)
                )
            case UserdataCmdsType.PROMPT:
                return PromptClient(
                    persona_info,
                    user_configs,
                    await self.get_namespace(persona_info)
                )
            case UserdataCmdsType.CONFIG:
                return ConfigClient(
                    persona_info,
                    user_configs,
                    await self.get_namespace(persona_info)
                )
            case UserdataCmdsType.PROGRAM:
                return ProgramDataClient(
                    persona_info,
                    user_configs,
                    await self.get_namespace(persona_info)
                )
            case _:
                raise ValueError("Invalid userdata_cmds_type")
    
    async def parser(self, branch_id: str, client: UserDataClient, send_msg: SendMsg):
        pass

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        msg = persona_info.message_stripped_str

        client = await self.get_client(persona_info)
        await self.parser(msg, client, send_msg)
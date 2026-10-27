import asyncio
from ....assist import PersonaInfo, SendMsg, Response
from ....cmd_info import CmdTypes
from ....command_register import(
    CommandCaller,
    CommandPackage
)
from ....clients import (
    ContextClient,
    PromptClient,
    ConfigClient,
    ProgramDataClient
)

@CommandCaller.register
class SessionBranchBind(CommandPackage):
    cmd = "sessionBranchBind"
    aliases = {
        "sbb",
        "SBB",
        "session_branch_bind",
        "Session_Branch_Bind",
        "SessionBranchBind",
        "SESSION_BRANCH_BIND",
    }
    cmd_type = CmdTypes.BRANCH_MIXED

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        user_configs = await persona_info.get_user_configs()
        dst_branch_id = persona_info.message_stripped_str
        context_client = ContextClient(persona_info, user_configs)
        prompt_client = PromptClient(persona_info, user_configs)
        config_client = ConfigClient(persona_info, user_configs)
        program_data_client = ProgramDataClient(persona_info, user_configs)
        tasks: list[tuple[asyncio.Task[Response[None]], str]] = []
        tasks.append(
            (
                asyncio.create_task(
                context_client.bind(dst_branch_id=dst_branch_id)
                ),
                "Context"
            )
        )
        tasks.append(
            (
                asyncio.create_task(
                prompt_client.bind(dst_branch_id=dst_branch_id)
                ),
                "Prompt"
            )
        )
        tasks.append(
            (
                asyncio.create_task(
                config_client.bind(dst_branch_id=dst_branch_id)
                ),
                "Config"
            )
        )
        tasks.append(
            (
                asyncio.create_task(
                program_data_client.bind(dst_branch_id=dst_branch_id)
                ),
                "ProgramData"
            )
        )
        await asyncio.gather(*[t[0] for t in tasks])
        await send_msg.send_multiple_responses(
            *[
                (t[0].result(), t[1])
                for t in tasks
            ]
        )
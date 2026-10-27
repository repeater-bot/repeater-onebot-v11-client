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
class DeleteSession(CommandPackage):
    cmd = "delSession"
    aliases = {
        "ds",
        "DS",
        "delete_session",
        "Delete_Session",
        "DeleteSession",
        "DELETE_SESSION",
    }
    cmd_type = CmdTypes.BRANCH_MIXED

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        user_configs = await persona_info.get_user_configs()
        context_client = ContextClient(persona_info, user_configs)
        prompt_client = PromptClient(persona_info, user_configs)
        config_client = ConfigClient(persona_info, user_configs)
        program_data_client = ProgramDataClient(persona_info, user_configs)
        tasks: list[tuple[asyncio.Task[Response[None]], str]] = []
        tasks.append(
            (
                asyncio.create_task(
                context_client.delete()
                ),
                "Context"
            )
        )
        tasks.append(
            (
                asyncio.create_task(
                prompt_client.delete()
                ),
                "Prompt"
            )
        )
        tasks.append(
            (
                asyncio.create_task(
                config_client.delete()
                ),
                "Config"
            )
        )
        tasks.append(
            (
                asyncio.create_task(
                program_data_client.delete()
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
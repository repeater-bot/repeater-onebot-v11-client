from ....assist import PersonaInfo, SendMsg
from ....cmd_info import CmdTypes
from ....command_register import(
    CommandCaller,
    CommandPackage
)
from ._matching import execute


@CommandCaller.register
class MatchContext(CommandPackage):
    cmd = "matchContext"
    aliases = {
        "mctx",
        "MCTX",
        "match_context",
        "Match_Context",
        "MatchContext",
        "MATCH_CONTEXT",
    }
    cmd_type = CmdTypes.CONTEXT
    description = f"""
    Match every context branch with a regular expression.
    The pattern must match from the start of each content (same as re.match).

    Usage:
    ```
    /{cmd} <regex>
    ```
    """

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        await execute(persona_info, send_msg, anchored = True)

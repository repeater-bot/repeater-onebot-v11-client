from ....assist import PersonaInfo, SendMsg
from ....cmd_info import CmdTypes
from ....command_register import(
    CommandCaller,
    CommandPackage
)
from ._matching import execute


@CommandCaller.register
class SearchContext(CommandPackage):
    cmd = "searchContext"
    aliases = {
        "sctx",
        "SCTX",
        "search_context",
        "Search_Context",
        "SearchContext",
        "SEARCH_CONTEXT",
    }
    cmd_type = CmdTypes.CONTEXT
    description = f"""
    Search every context branch with a regular expression.
    The pattern may match anywhere in the content (same as re.search).

    Usage:
    ```
    /{cmd} <regex>
    ```
    """

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        await execute(persona_info, send_msg, anchored = False)

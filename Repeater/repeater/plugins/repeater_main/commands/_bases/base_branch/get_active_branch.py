import re

from ....assist import PersonaInfo, SendMsg
from .base_branch import BaseBranch

class GetActiveBranch(BaseBranch):
    @classmethod
    def documents(cls):
        docs = [
            "Get active branch id",
            "",
            "Usage:",
            "```",
            f"/{cls.cmd}",
            "```"
        ]
        cls.description = "\n".join(docs)
        return cls.description

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        try:
            pattern = re.compile(persona_info.message_stripped_str)
        except re.error:
            await send_msg.send_error("Invalid regex pattern.")
        
        client = await self.get_client(persona_info)
        response = await client.get_active_branch()

        if response:
            await send_msg.send_text(f"Active branch id: {response}")
        else:
            await send_msg.send_error("No active branch found.")
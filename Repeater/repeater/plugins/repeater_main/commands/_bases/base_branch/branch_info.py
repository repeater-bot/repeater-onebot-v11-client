from ....assist import PersonaInfo, SendMsg
from .base_branch import BaseBranch

class BranchInfo(BaseBranch):
    @classmethod
    def documents(cls):
        docs = [
            "Gets metadata for the current active branch.",
            "",
            "Usage:",
            "```",
            f"/{cls.cmd}",
            "```"
        ]
        cls.description = "\n".join(docs)
        return cls.description
    
    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        client = await self.get_client(persona_info)
        response = await client.branch_info()
        if response:
            data = response.get_data()
            if data is None:
                await send_msg.send_error("Unable to process data.")
                send_msg.break_handler()

            text_buffer: list[str] = []
            text_buffer.append(f"Branch Type: {self.userdata_cmds_type.value}")
            text_buffer.append(f"Branch ID: {data.branch_id}")
            if data.file_exists:
                text_buffer.append(f"Branch Size: {data.size}")
                text_buffer.append(f"Branch Readable Size: {data.readable_size}")
                text_buffer.append(f"Branch Last Modified Time: {data.modified_datetime().strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                text_buffer.append("Branch File Not Exists")

            await send_msg.send_prompt("\n".join(text_buffer))
        else:
            await send_msg.send_response_check_code(response, f"Get {self.userdata_cmds_type.value} branch info failed")
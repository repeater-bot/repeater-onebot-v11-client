import asyncio
from ...assist import PersonaInfo, SendMsg, format_size_duration
from ...cmd_info import CmdTypes
from ...command_register import(
    CommandCaller,
    CommandPackage
)

@CommandCaller.register
class ClearAllSelfGroupFile(CommandPackage):
    cmd = "clearAllSelfGroupFile"
    aliases = {
        "casgf",
        "CASGF",
        "clear_all_self_group_file",
        "Clear_All_Self_Group_File",
        "ClearAllSelfGroupFile",
        "CLEAR_ALL_SELF_GROUP_FILE"
    }
    cmd_type = CmdTypes.PROTOCOL
    description = f"""
    Clear all self group files.

    Usage: 
    ```
    /{cmd}
    ```
    """

    @staticmethod
    def self_file_list(files: list[dict], uploader: str) -> list[dict]:
        return [
            file
            for file in files
            if file["uploader"] == int(uploader)
        ]

    @classmethod
    async def parse_folder(
        cls,
        persona_info: PersonaInfo,
        folder_id: str | None = None
    ):
        if folder_id:
            response = await persona_info.cached_api.get_group_files_by_folder(
                group_id = persona_info.group_id,
            )
        else:
            response = await persona_info.cached_api.get_group_root_files(
                group_id = persona_info.group_id,
            )

        files = response["files"]
        folders = response["folders"]

        self_files  = await asyncio.to_thread(
            cls.self_file_list,
            files,
            persona_info.self_id
        )

        total_size: int = 0
        tasks = []
        for file in self_files:
            total_size += file["file_size"]
            tasks.append(
                asyncio.create_task(
                    persona_info.cached_api.delete_group_file(
                        group_id = persona_info.group_id,
                        file_id = file["file_id"]
                    )
                )
            )
        step: int = 20
        for i in range(0, len(tasks), step):
            await asyncio.gather(*tasks[i:min(i+step, len(tasks))])
        
        if folders:
            total_size += sum(
                asyncio.gather(
                    *[
                        cls.parse_folder(persona_info, folder["folder_id"])
                        for folder in folders
                    ]
                )
            )
        return total_size
        

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        if not persona_info.is_group:
            await send_msg.send_error("Not in group")
            return

        if not persona_info.group_id:
            await send_msg.send_error("Not have group id")
            return
        total_size = await self.parse_folder(persona_info)
        await send_msg.send_prompt(f"Clear {format_size_duration(total_size, use_abbreviation = True)}")
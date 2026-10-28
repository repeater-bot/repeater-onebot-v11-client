from ...assist import PersonaInfo, SendMsg, Downloader, FileInfo
from ...clients import WorkspaceClient
from ...command_register import CommandCaller, CommandPackage
from ...cmd_info import CmdTypes

@CommandCaller.register
class UploadToWorkspace(CommandPackage):
    cmd = "uploadToWorkspace"
    aliases = {
        "utw",
        "UTW",
        "upload_to_workspace",
        "Upload_To_Workspace",
        "UploadToWorkspace",
        "UPLOAD_TO_WORKSPACE"
    }
    cmd_type = CmdTypes.WORKSPACE
    description = f"""
    Upload a file to the workspace.

    Usage:
    ```
    [reply file]
    /{cmd} <file_path>
    ```
    """
    def __init__(self):
        self.downloader = Downloader()

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        path = persona_info.message_stripped_str
        user_configs = await persona_info.get_user_configs()
        client = WorkspaceClient(persona_info, user_configs)
        
        files: list[FileInfo] = []
        for reply in await persona_info.from_reversed_reply_chain():
            files.extend(
                reply.get_file_infos()
            )
        files.extend(
            persona_info.get_file_infos()
        )

        if len(files) == 1:
            file = files[0]
            res = await client.write_file(
                path = path,
                data = await self.downloader.download_file(file.url),
            )
            await send_msg.send_prompt(f"Uploaded file to workspace, write {res.text} bytes to {path}")
        elif len(files) > 1:
            await send_msg.send_error("Too many files.")
        else:
            await send_msg.send_error("No file found.")
from ...assist import PersonaInfo, SendMsg, Downloader
from ...clients import WorkspaceClient
from ...command_register import CommandCaller, CommandPackage
from ...cmd_info import CmdTypes

@CommandCaller.register
class DownloadToWorkspace(CommandPackage):
    cmd = "downloadToWorkspace"
    aliases = {
        "dtw",
        "DTW",
        "download_to_workspace",
        "Download_To_Workspace",
        "DownloadToWorkspace",
        "DOWNLOAD_TO_WORKSPACE"
    }
    cmd_type = CmdTypes.WORKSPACE
    description = f"""
    Download a file from the workspace.

    Usage:
    ```
    /{cmd} <file_path>
    ```
    """
    def __init__(self):
        self.downloader = Downloader()

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        path = persona_info.message_stripped_str
        user_configs = await persona_info.get_user_configs()
        client = WorkspaceClient(persona_info, user_configs)
        exists = await client.exists(path)
        if not exists:
            await send_msg.send_text("Exists request failed.")
            return
        
        if exists.text != "true":
            await send_msg.send_text("File does not exist.")
            return
        
        file_url = client.file_url(path)
        await send_msg.send_file(
            url = file_url,
            file_name = path.split("/")[-1]
        )

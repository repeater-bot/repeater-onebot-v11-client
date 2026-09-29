from ...assist import PersonaInfo, SendMsg
from ...client_configs import storage_configs
from ...cmd_info import CmdTypes
from ...command_register import(
    CommandCaller,
    CommandPackage
)

@CommandCaller.register
class DeleteZone(CommandPackage):
    cmd = "deleteZone"
    aliases = {
        "dz",
        "DZ",
        "delete_zone",
        "Delete_Zone",
        "DeleteZone",
        "DELETE_ZONE",
    }
    cmd_type = CmdTypes.PROTOCOL
    description = f"""
    Delete a Qzone status.

    Usage: 
    ```
    /{cmd} status_tid
    ```
    """

    async def permissions_check(self, persona_info: PersonaInfo, send_msg: SendMsg):
        raw_result = await super().permissions_check(persona_info, send_msg)
        if raw_result and storage_configs.zone_sender_need_permission and not persona_info.has_super_permissions:
            return False
        return raw_result

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        tid = persona_info.message_stripped_str

        if not tid:
            await send_msg.send_prompt("Please input a valid status tid.")
            return

        result = await persona_info.cached_api.send_zone(
            tid = tid
        )

        await send_msg.send_prompt("Delete zone successfully.")
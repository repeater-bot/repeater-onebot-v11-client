from ...assist import PersonaInfo, SendMsg
from ...client_configs import storage_configs
from ...cmd_info import CmdTypes
from ...command_register import(
    CommandCaller,
    CommandPackage
)

@CommandCaller.register
class SendZone(CommandPackage):
    cmd = "sendZone"
    aliases = {
        "sz",
        "SZ",
        "send_zone",
        "Send_Zone",
        "SendZone",
        "SEND_ZONE",
    }
    cmd_type = CmdTypes.PROTOCOL
    description = f"""
    Pust a Qzone status.

    Usage: 
    ```
    /{cmd} content
    ```
    """

    async def permissions_check(self, persona_info: PersonaInfo, send_msg: SendMsg):
        raw_result = await super().permissions_check(persona_info, send_msg)
        if raw_result and storage_configs.zone_sender_need_permission and not persona_info.has_super_permissions:
            return False
        return raw_result

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        text = persona_info.message_stripped_str
        images = persona_info.get_images_url()

        result = await send_msg.send_zone(
            content = text,
            images = images,
            continue_handler = True
        )

        await send_msg.send_prompt(f"TID: {result}")
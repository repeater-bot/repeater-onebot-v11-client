import orjson
from ...assist import PersonaInfo, SendMsg
from ...cmd_info import CmdTypes
from ...command_register import(
    CommandCaller,
    CommandPackage
)

@CommandCaller.register
class UnpackForward(CommandPackage):
    cmd = "unpackForward"
    aliases = {
        "uf",
        "uf",
        "unpack_forward",
        "Unpack_Forward",
        "UnpackForward",
        "UNPACK_FORWARD"
    }
    cmd_type = CmdTypes.PROTOCOL
    description = f"""
    Unpack forward messages.

    Usage: 
    ```
    [reply to a forwarded message]
    /{cmd}
    ```
    or
    ```
    /{cmd} <forwarded message id>
    ```
    """
    
    async def parse_forward_msgs(
        self,
        persona_info: PersonaInfo,
        send_msg: SendMsg,
        forward_msg_id: str | None = None
    ) -> list[str]:
        return [
            "\n".join(
                [
                    f"{orjson.dumps(forward_msg.display_name).decode('utf-8')}: {orjson.dumps(forward_msg.message_cqcode).decode('utf-8')}"
                    for forward_msg in forward_msgs
                ]
            )
            for forward_msgs in await persona_info.from_forward_msgs(forward_msg_id)
        ]

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        forwards: list[str] = []
        text = persona_info.message_stripped_str

        if text:
            forward = await self.parse_forward_msgs(persona_info, send_msg, forward_msg_id = text)
            forwards.extend(forward)
        else:
            reply_msgs = await persona_info.from_reversed_reply_chain()
            for reply_msg in reply_msgs:
                forward = await self.parse_forward_msgs(reply_msg, send_msg)
                forwards.extend(forward)
            forward = await self.parse_forward_msgs(persona_info, send_msg)
            forwards.extend(forward)

        await send_msg.send_check_length_prompt(
            prompt = "\n\n---\n\n".join(forwards)
        )
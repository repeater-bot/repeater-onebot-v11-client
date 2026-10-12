from io import BytesIO
from ...assist import PersonaInfo, SendMsg
from ...cmd_info import CmdTypes
from ...command_register import(
    CommandCaller,
    CommandPackage
)
from ...clients import WatermarkClient

@CommandCaller.register
class WatermarkEncode(CommandPackage):
    cmd = "watermarkEncode"
    aliases = {
        "we",
        "WE",
        "watermark_encode",
        "Watermark_Encode",
        "WatermarkEncode",
        "WATERMARK_ENCODE",
    }
    cmd_type = CmdTypes.WATERMARK
    description = f"""
    Add a watermark to the image.

    Usage:
    ```
    /{cmd}
    ```
    """
    async def get_image_and_text(self, persona_info: PersonaInfo):
        images: list[str] = []
        text: list[str] = []
        for msg in await persona_info.from_reply_reversed_chain():
            images.extend(msg.get_images_url())
            text.append(msg.message_stripped_str)

        images.extend(persona_info.get_images_url())
        text.append(persona_info.message_stripped_str)
        return images, "\n\n".join(text)

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        user_configs = await persona_info.get_user_configs()
        client = WatermarkClient(persona_info, user_configs)
        images, text = await self.get_image_and_text(persona_info)
        if len(images) > 1:
            return await send_msg.send_error("Please send only one image at a time.")
        elif len(images) < 1:
            return await send_msg.send_error("Please send an image.")
        else:
            image = images[0]

        response = await client.encode(
            text,
            image,
        )

        if response:
            await send_msg.send_images(
                BytesIO(response.content)
            )
        else:
            await send_msg.send_error("Failed to encode image.")
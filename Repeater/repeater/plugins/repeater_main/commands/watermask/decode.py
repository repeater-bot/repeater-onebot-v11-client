from ...assist import PersonaInfo, SendMsg
from ...cmd_info import CmdTypes
from ...command_register import(
    CommandCaller,
    CommandPackage
)
from ...clients import WatermarkClient

@CommandCaller.register
class WatermarkDecode(CommandPackage):
    cmd = "watermarkDecode"
    aliases = {
        "wd",
        "WD",
        "watermark_decode",
        "Watermark_Decode",
        "WatermarkDecode",
        "WATERMARK_DECODE",
    }
    cmd_type = CmdTypes.WATERMARK
    description = f"""
    Decode the watermark from the image.

    Usage:
    ```
    /{cmd}
    ```
    """
    async def get_image_and_text(self, persona_info: PersonaInfo):
        images: list[str] = []
        for msg in await persona_info.from_reply_reversed_chain():
            images.extend(msg.get_images_url())

        images.extend(persona_info.get_images_url())
        return images

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        user_configs = await persona_info.get_user_configs()
        client = WatermarkClient(persona_info, user_configs)
        images = await self.get_image_and_text(persona_info)
        if len(images) > 1:
            return await send_msg.send_error("Please send only one image at a time.")
        elif len(images) < 1:
            return await send_msg.send_error("Please send an image.")
        else:
            image = images[0]

        response = await client.decode(
            image,
        )

        if response:
            data = response.get_data()
            if data is None:
                return await send_msg.send_error("Invalid response data.")
            await send_msg.send_text(data.text)
        else:
            await send_msg.send_error_render(
                response,
                break_code = 1
            )
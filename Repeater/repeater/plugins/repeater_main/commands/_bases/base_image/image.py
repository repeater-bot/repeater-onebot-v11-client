import base64

from ....assist import PersonaInfo, SendMsg
from ....cmd_info import CmdTypes
from ....command_register import(
    CommandCaller,
    CommandPackage
)
from ....clients import (
    ImageClient,
    Background,
    Moderation,
    OutputFormat,
    Quality,
    ImageResponseFormat,
    ImageSize,
    ImageStyle,

    UrlFile,
    PathFile,
    Base64File,
    FILE_TYPES
)
from ....client_configs import storage_configs, GenerateImageFileType
from ....logger import logger

class GenerateImageBase(CommandPackage):
    cmd_type = CmdTypes.GENIMG

    async def get_client(self, persona_info: PersonaInfo) -> ImageClient:
        user_configs = await persona_info.get_user_configs()
        return ImageClient(persona_info, user_configs)
    
    async def get_prompt(self, persona_info: PersonaInfo, send_msg: SendMsg) -> tuple[list[FILE_TYPES] | None, str]:
        prompts: list[str] = []

        images: list[FILE_TYPES] = []
        for reply in await persona_info.from_reply_reversed_chain(postcheck = True, break_chain = lambda reply: reply.is_self):
            prompts.append(reply.message_stripped_str)
            images.extend(await self.get_images(reply))
        images.extend(await self.get_images(persona_info))

        prompts.append(persona_info.message_stripped_str)
        prompt = "\n\n".join(prompts).strip()
        if not prompt:
            await send_msg.send_error("Error: No prompt provided")

        return images or None, prompt

    async def get_images(self, persona_info: PersonaInfo) -> list[FILE_TYPES]:
        images = []
        match storage_configs.generate_image_file_type:
            case GenerateImageFileType.URL:
                images.extend(
                    UrlFile(
                        url = image_url
                    )
                    for image_url in persona_info.get_images_url()
                )
            case GenerateImageFileType.PATH:
                images.extend(
                    PathFile(
                        path = image_url,
                    )
                    for image_url in persona_info.get_images_url()
                )
            case GenerateImageFileType.BASE64:
                images.extend(
                    Base64File(
                        data = image_url,
                    )
                    for image_url in persona_info.get_images_url()
                )
        return images
    
    async def generate_image(
            self,
            *,
            model_id: str | list[str] | None = None,
            images: list[FILE_TYPES] | None = None,
            prompt: str = "",
            
            background: Background | None = None,
            moderation: Moderation | None = None,
            n: int | None = None,
            output_compression: int | None = None,
            output_format: OutputFormat | None = None,
            partial_images: int | None = None,
            quality: Quality | None = None,
            response_format: ImageResponseFormat | None = None,
            size: ImageSize | str | None = None,
            style: ImageStyle | None = None,
            user: str | None = None,
            image_client: ImageClient,
            send_msg: SendMsg) -> list[str | bytes]:
        response = await image_client.generate(
            model_id = model_id,

            images = images,
            prompt = prompt,
            background = background,
            moderation = moderation,
            n = n,
            output_compression = output_compression,
            output_format = output_format,
            partial_images = partial_images,
            quality = quality,
            response_format = response_format,
            size = size,
            style = style,
            user = user,
        )

        if response:
            data = response.get_data()
            if data is None:
                await send_msg.send_error_response(response)
            else:
                gen_images: list[bytes | str] = []
                if data.data:
                    for index, image in enumerate(data.data):
                        if image.url is not None:
                            gen_images.append(
                                image.url
                            )
                        elif image.b64_json is not None:
                            gen_images.append(
                                base64.b64decode(image.b64_json)
                            )
                        else:
                            logger.warning(
                                "No image data found in response[{index}].",
                                index = index
                            )
                    return gen_images
                else:
                    await send_msg.send_error("No image data found in response.")
        else:
            await send_msg.send_error_response(response)

        assert False, "This line is never reached."

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        image_client = await self.get_client(persona_info)
        images, prompt = await self.get_prompt(persona_info, send_msg)
        output_images = await self.generate_image(
            images = images,
            prompt = prompt,
            image_client = image_client,
            send_msg = send_msg
        )
        await send_msg.send_images(*output_images)
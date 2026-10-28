import orjson
from typing import (
    AsyncGenerator,
    Union
)

from ...client_configs import *
from ...assist import Response, BaseClient
from ._request import ImagesRequest
from ._response import ImagesResponse
from .auxiliary import (
    Background,
    Moderation,
    OutputFormat,
    Quality,
    ImageResponseFormat,
    ImageSize,
    ImageStyle
)
from .file import FILE_TYPES
from ._partial_image_event import PartialImageEvent
from ._completed_image_event import CompletedImageEvent
from pydantic import ValidationError

class ImageClient(BaseClient):
    timeout = storage_configs.server_api_timeout.image

    async def generate(
            self,
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
        ) -> Response[ImagesResponse]:
        """Generate images from a prompt."""

        request = ImagesRequest(
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
            stream = False,
            style = style,
            user = user,
        )
        response = await self.client.post(
            url = self.join_url_static(IMAGE_ROUTE, self.namespace),
            json = request.model_dump(exclude_none = True),
        )
        return Response(
            httpx_response = response,
            model = ImagesResponse
        )

    async def generate_stream(
            self,
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
        ) -> AsyncGenerator[PartialImageEvent | CompletedImageEvent, None]:
        """Generate images from a prompt."""

        request = ImagesRequest(
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
            stream = True,
            style = style,
            user = user,
        )
        async with self.client.stream(
            "POST",
            url = self.join_url_static(IMAGE_ROUTE, self.namespace),
            json = request.model_dump(),
        ) as response:
            response.raise_for_status()

            async for line in response.aiter_lines():
                if line:
                    data = orjson.loads(line)
                    try:
                        model = PartialImageEvent.model_validate(data)
                    except ValidationError as e:
                        try:
                            model = CompletedImageEvent.model_validate(data)
                        except ValidationError as e:
                            raise ValueError("Invalid event type") from e
                    yield model
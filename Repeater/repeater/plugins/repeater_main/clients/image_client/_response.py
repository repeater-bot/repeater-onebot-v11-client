from pydantic import BaseModel, ConfigDict
from .auxiliary import (
    Image,
    Background,
    OutputFormat,
    Quality,
    ImageSize,
    ImageTokenUsage,
)

class ImagesResponse(BaseModel):
    model_config = ConfigDict(
        validate_assignment = True
    )

    created: int = 0
    background: str | None = None
    data: list[Image] | None = None
    output_format: str | None = None
    quality: str | None = None
    size: str | None = None
    usage: ImageTokenUsage | None = None
from pydantic import BaseModel, ConfigDict
from .auxiliary.background import Background
from .auxiliary.output_format import OutputFormat
from .auxiliary.quality import Quality
from .auxiliary.size import ImageSize
from typing import Literal

class PartialImageEvent(BaseModel):
    model_config = ConfigDict(
        validate_assignment = True
    )

    b64_json: str | None = None
    background: str | None = None
    created_at: int | None = None
    output_format: str | None = None
    partial_image_index: int | None = None
    quality: str | None = None
    size: str | None = None
    type: Literal["image_generation.partial_image"] = "image_generation.partial_image"
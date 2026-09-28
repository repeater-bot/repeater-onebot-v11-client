from pydantic import BaseModel
from .image_usage_tokens_details import ImageUsageTokensDetails

class ImageTokenUsage(BaseModel):
    input_tokens: int | None = None
    input_tokens_details: ImageUsageTokensDetails | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None
    output_tokens_details: ImageUsageTokensDetails | None = None

    def to_string(self, indent: int = 0) -> str:
        buffer: list[str] = []

        buffer.append(f"Input Usage: {self.input_tokens}")
        if self.input_tokens_details is not None:
            if self.input_tokens_details.image_tokens is not None:
                buffer.append(f"  Input Images: {self.input_tokens_details.image_tokens}")
            if self.input_tokens_details.text_tokens is not None:
                buffer.append(f"  Input Text: {self.input_tokens_details.text_tokens}")
        buffer.append(f"Output Usage: {self.output_tokens}")
        if self.output_tokens_details is not None:
            if self.output_tokens_details.image_tokens is not None:
                buffer.append(f"  Output Images: {self.output_tokens_details.image_tokens}")
            if self.output_tokens_details.text_tokens is not None:
                buffer.append(f"  Output Text: {self.output_tokens_details.text_tokens}")
        buffer.append(f"Total Usage: {self.total_tokens}")

        return (" " * indent) + ((" " * indent) + "\n").join(buffer)
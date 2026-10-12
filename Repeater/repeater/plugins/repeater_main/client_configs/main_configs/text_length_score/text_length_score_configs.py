from pydantic import BaseModel, Field
from .text_length_score_threshold import TextLengthScoreThreshold

class TextLengthScoreConfigs(BaseModel):
    max_lines: int = 5
    single_line_max: int = 64
    mean_line_max: int = 24
    total_length: int = 400
    threshold: TextLengthScoreThreshold = Field(default_factory = TextLengthScoreThreshold)
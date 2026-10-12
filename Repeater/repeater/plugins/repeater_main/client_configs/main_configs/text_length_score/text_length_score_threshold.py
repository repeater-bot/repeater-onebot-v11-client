from pydantic import BaseModel

class TextLengthScoreThreshold(BaseModel):
    group: float = 1.0
    private: float = 2.48
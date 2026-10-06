from pydantic import BaseModel

class WatermaskEncodeRequest(BaseModel):
    image: str
    text: str | None = None

class WatermaskDecodeRequest(BaseModel):
    image: str
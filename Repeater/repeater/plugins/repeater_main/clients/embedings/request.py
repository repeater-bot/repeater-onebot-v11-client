from pydantic import BaseModel

class SimilarityRequest(BaseModel):
    model: str | None = None
    first_text: str | None = None
    second_text: str | None = None

class VectorsRequest(BaseModel):
    model: str | None = None
    texts: list[str] | None = None
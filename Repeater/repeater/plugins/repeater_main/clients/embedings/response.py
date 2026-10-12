from pydantic import BaseModel

class SimilarityResponse(BaseModel):
    similarity: float
    first_text: str
    second_text: str

class VectorsResponse(BaseModel):
    vectors: list[list[float]]
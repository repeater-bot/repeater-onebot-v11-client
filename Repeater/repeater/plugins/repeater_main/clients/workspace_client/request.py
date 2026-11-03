from pydantic import BaseModel

class DestinationRequest(BaseModel):
    destination: str

class EditRequest(BaseModel):
    start: int
    end: int
    data: str

class CopyRangeRequest(BaseModel):
    destination: str
    start: int
    end: int

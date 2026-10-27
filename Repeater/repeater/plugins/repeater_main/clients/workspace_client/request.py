from pydantic import BaseModel

class DestinationRequest(BaseModel):
    destination: str

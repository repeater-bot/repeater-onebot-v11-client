from pydantic import BaseModel


class RefreshResponse(BaseModel):
    message: str = "Models refreshed successfully"
    status: str = "success"
from pydantic import BaseModel

class ExternalTriggerRequest(BaseModel):
    """
    External trigger request model
    """
    bot_id: str
    handler: str
    namespace: str
    args: str | None = None
    
    font: int = 0
    nickname: str | None = None
    sex: str | None = None
    age: int | None = None
    card: str | None = None
    area: str | None = None
    level: str | None = None
    role: str | None = None
    title: str | None = None
    to_me: bool = False
    sub_type: str = "normal"
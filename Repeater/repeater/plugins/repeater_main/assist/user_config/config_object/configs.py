from pydantic import BaseModel
from ....client_configs import HelloContent
from .chat_output import ChatOutputMode

class UserConfigs(BaseModel):
    backend: str | None = None
    hello_content: HelloContent | None = None
    chat_output: ChatOutputMode = ChatOutputMode.AUTO
    variables: dict | None = None
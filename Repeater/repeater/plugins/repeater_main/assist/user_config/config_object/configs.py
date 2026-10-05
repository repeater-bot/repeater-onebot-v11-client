from pydantic import BaseModel, Field
from ....client_configs import HelloContent
from .chat_output import ChatOutput

class UserConfigs(BaseModel):
    backend: str | None = None
    hello_content: HelloContent | None = None
    chat_output: ChatOutput = Field(default_factory=ChatOutput)
    variables: dict | None = None
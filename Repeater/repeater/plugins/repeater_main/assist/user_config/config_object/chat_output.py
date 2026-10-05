from pydantic import BaseModel
from ....client_configs import ChatOutputMode

class ChatOutput(BaseModel):
    reasoning_content: ChatOutputMode | None = None
    tool_content: ChatOutputMode | None = None
    content: ChatOutputMode | None = None
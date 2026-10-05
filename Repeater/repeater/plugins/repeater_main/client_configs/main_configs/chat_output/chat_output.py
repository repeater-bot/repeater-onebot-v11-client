from pydantic import BaseModel
from .chat_output_mode import ChatOutputMode

class ChatOutput(BaseModel):
    reasoning_content: ChatOutputMode = ChatOutputMode.IMAGE
    tool_content: ChatOutputMode = ChatOutputMode.IMAGE
    content: ChatOutputMode = ChatOutputMode.AUTO
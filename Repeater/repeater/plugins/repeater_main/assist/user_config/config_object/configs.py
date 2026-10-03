from pydantic import BaseModel
from ....client_configs import HelloContent

class UserConfigs(BaseModel):
    backend: str | None = None
    hello_content: HelloContent | None = None
    smart_at_output: bool = True
    variables: dict | None = None
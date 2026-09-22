from pydantic import BaseModel

class ExternalTriggerServer(BaseModel):
    """
    External trigger server configuration.
    """
    enabled: bool = False
    host: str = "localhost"
    port: int = 5000
from pydantic import BaseModel

class ExternalTriggerServer(BaseModel):
    """
    External trigger server configuration.
    """
    enabled: bool = False
    host: str = "127.0.0.1"
    port: int = 5000
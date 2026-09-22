from pydantic import BaseModel

class ExternalTriggerServer(BaseModel):
    """
    External trigger server configuration.
    """
    host: str = "localhost"
    port: int = 5000
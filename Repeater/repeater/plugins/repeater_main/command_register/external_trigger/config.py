import secrets
from nonebot import get_plugin_config
from pydantic import BaseModel, Field

class ExternalTriggerConfig(BaseModel):
    external_trigger_token: str = Field(default_factory=lambda: f"ets-{secrets.token_urlsafe(32)}")

external_trigger_config = get_plugin_config(ExternalTriggerConfig)
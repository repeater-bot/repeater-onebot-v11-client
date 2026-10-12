from pydantic import BaseModel, Field
from .throw_on_duplicate import ThrowOnDuplicate

class LoadingConfigs(BaseModel):
    throw_on_duplicate: ThrowOnDuplicate = Field(default_factory = ThrowOnDuplicate)
    continue_on_error: bool = Field(default = False)
    recommended_class_name_is_trigger: bool = Field(default = True)
    component_is_trigger: bool = Field(default = True)
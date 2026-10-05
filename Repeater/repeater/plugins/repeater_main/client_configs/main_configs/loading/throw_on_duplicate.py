from pydantic import BaseModel

class ThrowOnDuplicate(BaseModel):
    trigger: bool = True
    handler: bool = True
    matcher: bool = True
    type: bool = True
    component: bool = True
    class_name: bool = True
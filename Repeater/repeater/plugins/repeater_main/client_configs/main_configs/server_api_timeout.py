from pydantic import BaseModel

class ServerAPITimeout(BaseModel):
    chat: int | float | None = 4800.0
    image: int | float | None = 2400.0
    similarity: int | float | None = 600.0
    context: int | float | None = 10.0
    prompt: int | float | None = 10.0
    config: int | float | None = 10.0
    data_manager: int | float | None = 10.0
    licenses: int | float | None = 10.0
    model_info: int | float | None = 1200.0
    status: int | float | None = 10.0
    version: int | float | None = 10.0
    request_log: int | float | None = 1200.0
    variable_expansion: int | float | None = 40.0
    render: int | float | None = 600.0
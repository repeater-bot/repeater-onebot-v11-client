from pydantic import BaseModel
from ...cmd_info import CmdTypes
from typing import Literal

class BehavioralACT(BaseModel):
    allowed_cmd_types: list[str | CmdTypes] | Literal["ALL"] = "ALL"
    block_handlers: bool = False
    block_output: bool = False
    block_send_request: bool = False

    def check_cmd_types_allowed(self, cmd_type: str | CmdTypes) -> bool:
        if self.allowed_cmd_types == "ALL":
            return True
        return cmd_type in self.allowed_cmd_types
from pydantic import BaseModel, Field
from enum import StrEnum
from ...content_role import ContentRole
from ...content_unit import ContentUnit

class WithdrawResponse(BaseModel):
    status: str = "success"
    deleted: int = 0
    deleted_context: list[ContentUnit] = Field(default_factory=list)
    delete_context_pair: int = 0
    context: list[ContentUnit] = Field(default_factory=list)

class ContextTotalLengthResponse(BaseModel):
    total_context_length: int = 0
    context_length: int = 0
    average_content_length: float = 0.0

class RoleStructureCheckerResponse(BaseModel):
    message: str = "No role structure error found"
    index: int = -1
    role: ContentRole | None = None
    expected_role: list[ContentRole] | None = None

class ContextPairsResponse(BaseModel):
    context_pairs: list[list[ContentUnit]] = Field(default_factory=list)
    length: int = 0
    context_length: int = 0
    total_character_length: int = 0
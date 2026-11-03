from pydantic import BaseModel, Field


class ContextSearchConfigs(BaseModel):
    """
    Tunables for context regex search (searchContext / matchContext)
    """
    max_pattern_chars: int = Field(default = 256, ge = 1)
    """Maximum length of a user supplied regex"""

    match_timeout: int | float = Field(default = 2.0, gt = 0)
    """Upper bound in seconds for a single match, guarding against exponential backtracking"""

    branch_concurrency: int = Field(default = 8, ge = 1)
    """Number of branches fetched concurrently"""

    max_reported_branches: int = Field(default = 20, ge = 1)
    """Maximum number of branches listed in the report"""

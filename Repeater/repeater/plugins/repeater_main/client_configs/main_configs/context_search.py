from pydantic import BaseModel, Field


class ContextSearchConfigs(BaseModel):
    """
    上下文正则检索（searchContext / matchContext）的可调参数
    """
    max_pattern_chars: int = Field(default = 256, ge = 1)
    """用户正则的最大长度"""

    match_timeout: int | float = Field(default = 2.0, gt = 0)
    """单次匹配的时间上限（秒），用于兜住指数级回溯"""

    branch_concurrency: int = Field(default = 8, ge = 1)
    """同时拉取的分支数"""

    max_reported_branches: int = Field(default = 20, ge = 1)
    """报告里最多列出的分支数"""

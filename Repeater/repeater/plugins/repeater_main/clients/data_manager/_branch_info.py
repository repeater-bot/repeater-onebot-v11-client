from pydantic import BaseModel
from datetime import datetime
from ...assist import format_carry_duration, Preset, Level, FinalLevel
from ...client_configs import storage_configs

SIZE_PRESET = Preset(
    levels=[
        Level("Bytes", "B", 1024),
        Level("Kibibyte", "KiB", 1024),
        Level("Mebibyte", "MiB", 1024),
        Level("Gibibyte", "GiB", 1024),
        Level("Tebibyte", "TiB", 1024),
        Level("Pebibyte", "PiB", 1024),
        Level("Exbibyte", "EiB", 1024),
    ],
    final_level = FinalLevel("Yobibyte", "YiB")
)

class BranchInfo(BaseModel):
    """Branch Info"""
    branch_id: str = ""
    size: int = 0
    modified_time: float = 0
    file_exists: bool = False

    def modified_datetime(self) -> datetime:
        return datetime.fromtimestamp(self.modified_time)
    
    @property
    def readable_size(self) -> str:
        return format_carry_duration(
            value = self.size,
            preset = SIZE_PRESET,
            use_abbreviation = storage_configs.branch_file_size_use_abbreviation
        )

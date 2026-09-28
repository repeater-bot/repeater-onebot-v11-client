from dataclasses import dataclass, field

@dataclass(frozen=True)
class Level:
    """
    Format Carry Duration Preset Level Unit
    """
    name: str
    abbr: str
    divisor: int

@dataclass(frozen=True)
class FinalLevel:
    """
    Format Carry Duration Preset Final Level
    """
    name: str
    abbr: str

@dataclass(frozen=True)
class Preset:
    """
    Format Carry Duration Preset
    """

    levels: list[Level] = field(default_factory=list)
    start_with: int = 0
    delimiter: str = ", "
    final_level: FinalLevel = field(default=FinalLevel("max_level", "max"))
    negative_prompt: str = "(Negative) "
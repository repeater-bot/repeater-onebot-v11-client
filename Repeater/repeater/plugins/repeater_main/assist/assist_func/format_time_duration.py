from .format_carry_duration import format_carry_duration, Preset, Level, FinalLevel

NS_TIME_PRESET = Preset(
    levels = [
        Level("nanosecond", "ns", 1000),
        Level("microsecond", "μs", 1000),
        Level("millisecond", "ms", 1000),
        Level("second", "s", 60),
        Level("minute", "min", 60),
        Level("hour", "h", 24),
        Level("day", "day", 30),
        Level("month", "mon", 12),
        Level("year", "y", 10),
        Level("decade", "dec", 10),
    ],
    final_level = FinalLevel(
        name = "century",
        abbr = "c"
    )
)

TIME_PRESET = Preset(
    levels =  [
        Level("second", "s", 60),
        Level("minute", "min", 60),
        Level("hour", "h", 24),
        Level("day", "day", 30),
        Level("month", "mon", 12),
        Level("year", "y", 100),
        Level("decade", "dec", 10),
    ],
    final_level = FinalLevel(
        name = "century",
        abbr = "c"
    )
)

def format_time_duration_ns(duration: int | float, use_abbreviation: bool = False) -> str:
    """
    Format time duration in nanoseconds to a human-readable string.
    """
    return format_carry_duration(
        value = duration,
        preset = NS_TIME_PRESET,
        use_abbreviation = use_abbreviation,
    )

def format_time_duration(duration: int | float, use_abbreviation: bool = False) -> str:
    """
    Format time duration in seconds to a human-readable string.
    """
    return format_carry_duration(
        value = duration,
        preset = TIME_PRESET,
        use_abbreviation = use_abbreviation,
    )
from .format_carry_duration import format_carry_duration, Preset, Level, FinalLevel

SIZE_PRESET = Preset(
    levels = [
        Level("Bytes", "B", 1024),
        Level("Kibibyte", "KiB", 1024),
        Level("Mebibyte", "MiB", 1024),
        Level("Gibibyte", "GiB", 1024),
        Level("Tebibyte", "TiB", 1024),
        Level("Pebibyte", "PiB", 1024),
        Level("Exbibyte", "EiB", 1024),
        Level("Zebibyte", "ZiB", 1024),

    ],
    final_level = FinalLevel(
        name = "Yobibyte",
        abbr = "YiB"
    )
)


def format_size_duration(duration: int | float, use_abbreviation: bool = False) -> str:
    """
    Format size duration in seconds to a human-readable string.
    """
    return format_carry_duration(
        value = duration,
        preset = SIZE_PRESET,
        use_abbreviation = use_abbreviation,
    )
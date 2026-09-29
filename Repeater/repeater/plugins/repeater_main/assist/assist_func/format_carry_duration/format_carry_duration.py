from .base_preset import Preset

def format_carry_duration(
    value: int | float,
    preset: Preset,
    use_abbreviation: bool = False,
) -> str:
    """
    Format a value using a carry system with specified levels.

    Args:
        value (int): The value to format.
        preset (BasePreset): The preset to use for formatting.
        use_abbreviation (bool, optional): Whether to use abbreviations. Defaults to False.

    Returns:
        str: Formatted value string.
    """
    if not preset.levels:
        raise ValueError("levels cannot be empty")
    
    if preset.start_with not in range(len(preset.levels)):
        raise ValueError(f"start_with must be in range [0, {len(preset.levels)})")
    
    # Handle zero value
    if value == 0:
        name= preset.levels[0].name
        abbr = preset.levels[0].abbr
        return f"0 {abbr if use_abbreviation else name}"
    
    # Handle negative value
    is_negative = value < 0
    value = abs(value)
    
    data_level_stack: list[str] = []
    remaining_part: int | float = value
    
    # Process each level starting from the specified level
    for index, level in enumerate(preset.levels[preset.start_with:]):
        if remaining_part == 0:
            break
            
        current_value = remaining_part % level.divisor
        remaining_part //= level.divisor
        
        if current_value > 0:
            unit = level.abbr if use_abbreviation else level.name
            # Handle pluralization
            if current_value != 1 and not use_abbreviation:
                unit += "s"
            if index != 0:
                current_value = int(current_value)
            data_level_stack.append(f"{current_value} {unit}")
        
        if remaining_part == 0:
            break
    
    # Handle the final level
    if remaining_part > 0:
        unit = preset.final_level.abbr if use_abbreviation else preset.final_level.name
        data_level_stack.append(f"{int(remaining_part)} {unit}")
    
    # Reverse the stack to get the correct order (largest to smallest)
    text = preset.delimiter.join(data_level_stack[::-1])
    
    if is_negative:
        text = f"{preset.negative_prompt}{text}"
    
    return text
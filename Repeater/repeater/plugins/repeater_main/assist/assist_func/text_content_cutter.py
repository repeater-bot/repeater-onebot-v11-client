def text_content_cutter(
        text: str,
        max_length: int | None,
        abbreviation: str = "...",
    ) -> str:
    """
    Cut text to max length
    """

    if max_length is None:
        return text
    
    max_length -= len(abbreviation)
    
    if len(text) > max_length:
        if max_length > 6:
            return text[:max_length - 6] + abbreviation + text[-3:]
        elif max_length > 3:
            return text[:max_length - 3] + abbreviation
        else:
            return abbreviation
    else:
        return text
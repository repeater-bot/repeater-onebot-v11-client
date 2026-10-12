from .._bases import BaseFIM
from ...command_register import CommandCaller

@CommandCaller.register
class FillAtAfter(BaseFIM):
    cmd = "fillAtAfter"
    aliases = {
        "faa",
        "FAA",
        "fill_at_after",
        "Fill_At_After",
        "FillAtAfter",
        "FILL_AT_AFTER"
    }
    description = f"""
        Given a prefix, let AI write the following.
        
        Usage:
        ```
        /{cmd} text
        ```
    """
    echo = True
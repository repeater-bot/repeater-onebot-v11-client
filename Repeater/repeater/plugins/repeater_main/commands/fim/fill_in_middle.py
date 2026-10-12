from .._bases import BaseFIM
from ...command_register import CommandCaller

@CommandCaller.register
class FillInMiddle(BaseFIM):
    cmd = "fillInMiddle"
    aliases = {
        "fim",
        "FIM",
        "fill_in_middle",
        "Fill_In_Middle",
        "FillInMiddle",
        "FILL_IN_MIDDLE"
    }
    description = f"""
        Use The [fill_this] tag or three underscores to mark the spaces and let the AI fill them.
        
        Usage:
        ```
        /{cmd} text
        ```
    """
import re
from ...assist import PersonaInfo, Variables

pattern = re.compile(r"\{\s*var\s*:\s*([\w\.]+)\s*\}")

def fill_var(info: PersonaInfo, vars: Variables) -> PersonaInfo:
    """
    Fill variables with the given values.
    """

    def _fill_var(match_group: re.Match[str]) -> str:
        nonlocal vars
        variables = vars.copy()
        var_name = match_group.group(1)
        return variables.get(var_name, "")

    messages: list[str] = info.message_cqcode.split("\n")  # 不能用 splitlines(): 它会把 \v \f \r \x1c \u2028 等也当成换行
    new_messages: list[str] = []
    for line in messages:
        if not line.startswith(" "):
            new_line = pattern.sub(_fill_var, line)
            new_messages.append(new_line)
        else:
            new_messages.append(line)

    copyed_info = info.copy(
        args = info.make_message(
            message = "\n".join(new_messages)
        )
    )
    return copyed_info
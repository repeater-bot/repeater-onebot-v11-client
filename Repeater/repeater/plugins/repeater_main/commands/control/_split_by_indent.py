"""按缩进切分消息。

对外只暴露 :func:`split_by_indent`：把一条消息切成
``[触发行, 该触发行全部直接子行合并成的参数]``，一次只解析一层。
更深的层级由子块本身作为参数再次进入本函数解析。
"""

from nonebot.adapters.onebot.v11 import Message, MessageSegment


class IndentError(ValueError):
    """缩进不合法。

    继承 ``ValueError``，调用方按 ``ValueError`` 捕获即可。
    """

    def __init__(self, line_no: int, detail: str) -> None:
        self.line_no = line_no
        self.detail = detail
        super().__init__(f"[line {line_no}] {detail}")


def split_by_indent(
    message: Message | str,
    indent: int = 2,
    indent_char: str = " ",
) -> list[list[Message]]:
    """按缩进把消息切成块，每个块是 ``[触发行, 子块（可选）]``。

    规则：

    - 行首空白必须完全由 ``indent_char`` 组成，宽度必须是 ``indent`` 的整数倍，
      否则抛 :class:`IndentError`；
    - 缩进为 0 的行开启新块；缩进不为 0 的行剥掉恰好一级缩进（``indent`` 个
      ``indent_char``）后归入当前块的子块，剩余缩进原样保留；
    - 第一个非空行就是缩进行时抛 :class:`IndentError`，不会静默丢弃；
    - 空行与纯空白行被忽略，既不产生块也不打断当前块；
    - 子块是一个 ``Message``：各子行原样拼接，行间插入一个 ``"\\n"`` 文本段。

    切分完全在消息段层面进行，不做 CQ 码字符串往返，因此行内除 ``"\\n"`` 以外
    的字符（含 CQ 码参数里的字符）不会造成额外断行；返回的 ``Message`` 也不与
    入参共享任何消息段。
    """
    if indent <= 0:
        raise ValueError("indent must be greater than 0")
    if len(indent_char) != 1:
        raise ValueError("indent_char must be a single character")

    if isinstance(message, str):
        message = Message(message)

    results: list[list[Message]] = []
    current_root: Message | None = None
    current_children: list[Message] = []

    for line_no, line in enumerate(_split_lines(message), start=1):
        if _is_blank(line):
            continue

        leading, bad_char = _measure_indent(line, indent_char)
        if bad_char is not None:
            raise IndentError(
                line_no,
                f"indentation uses {bad_char!r}, only {indent_char!r} is allowed",
            )
        if leading % indent:
            raise IndentError(
                line_no,
                f"indentation is {leading} characters, must be a multiple of {indent}",
            )

        if leading == 0:
            if current_root is not None:
                results.append(_make_block(current_root, current_children))
            current_root = line
            current_children = []
            continue

        if current_root is None:
            raise IndentError(
                line_no, "line is indented but no top-level line precedes it"
            )
        current_children.append(_strip_leading_text(line, indent))

    if current_root is not None:
        results.append(_make_block(current_root, current_children))

    return results


def _split_lines(message: Message) -> list[Message]:
    """按 ``"\\n"`` 把消息切成若干行，非文本段归属它所在的行。

    ``"\\r\\n"`` 与单独的 ``"\\r"`` 都算一次换行；其余字符（例如 ``"\\v"``）
    不再被当作换行。
    """
    lines: list[Message] = [Message()]

    for segment in message:
        if not segment.is_text():
            lines[-1].append(segment.copy())
            continue

        text = segment.data.get("text", "")
        if not isinstance(text, str):
            raise TypeError("text segment must be str")

        text = text.replace("\r\n", "\n").replace("\r", "\n")
        for index, part in enumerate(text.split("\n")):
            if index:
                lines.append(Message())
            if part:
                lines[-1].append(MessageSegment.text(part))

    return lines


def _is_blank(line: Message) -> bool:
    """整行只有空白文本、且不含非文本段时视为空行。"""
    for segment in line:
        if not segment.is_text():
            return False
        text = segment.data.get("text", "")
        if text and not text.isspace():
            return False
    return True


def _measure_indent(line: Message, indent_char: str) -> tuple[int, str | None]:
    """返回 ``(行首空白宽度, 第一个不是 indent_char 的空白字符)``。

    只有行首的文本段可能承载缩进；行首不是文本段时缩进为 0。
    """
    if not line or not line[0].is_text():
        return 0, None

    leading = 0
    for char in line[0].data.get("text", ""):
        if not char.isspace():
            break
        if char != indent_char:
            return leading, char
        leading += 1

    return leading, None


def _strip_leading_text(message: Message, count: int) -> Message:
    """裁掉行首 ``count`` 个字符，只作用于文本段。

    被整段裁完的文本段会被丢弃，非文本段原样保留，因此段结构不会丢失。
    """
    result = Message()

    for segment in message:
        if count > 0 and segment.is_text():
            text = segment.data.get("text", "")
            if len(text) <= count:
                count -= len(text)
                continue
            result.append(MessageSegment.text(text[count:]))
            count = 0
        else:
            result.append(segment.copy())

    return result


def _make_block(root: Message, children: list[Message]) -> list[Message]:
    """把触发行与它的子行组装成一个块，没有子行时只返回触发行。"""
    if not children:
        return [root]

    child = Message()
    for index, line in enumerate(children):
        if index:
            child.append(MessageSegment.text("\n"))
        child.extend(line)

    return [root, child]

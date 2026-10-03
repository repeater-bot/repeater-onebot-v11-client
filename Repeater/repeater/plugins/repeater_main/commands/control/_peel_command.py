"""从块里剥离出"命令名 + 参数"。

``silence`` / ``execute`` / ``bypass`` / ``debug_mode`` / ``flip_result`` 这类控制
命令的输入是一个"触发行 + 缩进子块"的块：第一行的第一个 token 是命令名，其余
是它的参数。

两个坑：

1. 不能在整块字符串上做 ``^(token)\\s*(?P<args>.*)$``：``\\s*`` 只会吃掉紧跟
   命令名的那一个换行与缩进，后面几行的缩进会原样留下，于是多行参数块整体错位
   一级，第二行起的内容会被误判成第一行的子行。
2. 不要用正则去抠命令名：前缀来自驱动配置的 ``command_start``
   (:meth:`CommandCaller.cmd_prefixs`)，可能是 ``/`` 之外的字符、可能多个，写死
   字符类会漏，逐个拼正则又要处理转义。这里全部用字符串切分，前缀是否合法交给
   调用方的匹配函数判定。
"""

from nonebot.adapters.onebot.v11 import Message, MessageSegment

from ._split_by_indent import split_by_indent, strip_leading_text


def peel_command(message: Message | str) -> tuple[str, Message] | None:
    """取出块里的命令名与它的参数。

    :param message: 参数块
    :return: ``(命令名, 参数)``，不合法时返回 ``None``

    命令名 = 行首到第一个空白为止的整段文本（与 ``_parse_input`` 的取法一致），
    带不带命令前缀都可以，由调用方的匹配函数决定认不认。参数 = 触发行的行内
    参数 + 一级缩进后的子块，行间以 ``"\\n"`` 连接，与
    :func:`~._split_by_indent.split_by_indent` 的缩进语义一致。

    返回 ``None`` 的两种情况：行首取不到命令名（空消息、以空白开头、或以非文本
    段开头）；或者存在多于一个顶级块（这些命令只接受一条命令）。
    """
    blocks = split_by_indent(message)
    if len(blocks) != 1:
        return None

    head, *children = blocks[0]
    peeled_head = _peel_head(head)
    if peeled_head is None:
        return None

    token, consumed = peeled_head
    args = strip_leading_text(head, consumed)

    child_segments = [segment for child in children for segment in child]
    if args and child_segments:
        args.append(MessageSegment.text("\n"))
    args.extend(child_segments)

    return token, args


def _peel_head(head: Message) -> tuple[str, int] | None:
    """取出行首命令名，以及它连同其后空白占掉的文本字符数。

    只拼行首连续的文本段，遇到第一个非文本段就停：命令名不跨消息段，非文本段
    两侧的空白也不会被拼到一起（否则 ``/echo [CQ:image,...] hi`` 的参数会丢掉
    那个空格）。
    """
    text = ""
    for segment in head:
        if not segment.is_text():
            break
        text += segment.data.get("text", "")

    if not text or text[0].isspace():
        return None

    end = 0
    while end < len(text) and not text[end].isspace():
        end += 1

    consumed = end
    while consumed < len(text) and text[consumed].isspace():
        consumed += 1

    return text[:end], consumed

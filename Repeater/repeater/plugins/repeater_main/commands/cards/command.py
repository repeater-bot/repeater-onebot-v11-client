"""FindCards 命令：按名称检索卡图，并把新卡图加进卡牌库。

命令注册走 @CommandCaller.register + CommandPackage；发送走 SendMsg；
取图引用走 PersonaInfo.get_images_url；消息组装走 PersonaInfo.make_message，
最终由 send_msg.send_any 一次性发出（名称与卡图是同一条消息）。
"""

from __future__ import annotations

import asyncio
import random
import re
import textwrap
from typing import Final, Sequence

from nonebot.adapters.onebot.v11 import MessageSegment

from ...assist import PersonaInfo, SendMsg
from ...cmd_info import CmdTypes
from ...command_register import CommandCaller, CommandPackage
from ...logger import logger

from .constants import (
    FUZZY_CUTOFF,
    IMAGE_WAIT_TIMEOUT,
    LIST_LIMIT,
    SAME_NAME_LIMIT,
)
from .library import LIBRARY, ConverterMissing
from .matching import Match, search
from .models import Card

_ADD_FLAGS: Final[tuple[str, ...]] = ("--add", "-add", "-a")
"""添加卡图的参数前缀；长前缀放前面，避免被短前缀截断。"""

_SPEC_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"""["']?\s*(zh|en)\s*["']?\s*[=:]\s*(?:"([^"]*)"|'([^']*)'|([^,;}\n]*))""",
    re.IGNORECASE
)
"""解析 {"zh": "中文名", "en": "English"}；中文引号会先被翻译成 ASCII。"""

_QUOTE_TRANSLATION: Final[dict[int, str | int | None]] = str.maketrans(
    {
        "\u201c": '"',
        "\u201d": '"',
        "\u2018": "'",
        "\u2019": "'",
        "\uff1a": ":",
        "\uff1d": "=",
        "\uff0c": ",",
        "\u3000": " ",
    }
)
"""全角引号/冒号/等号/逗号/空格 -> ASCII，方便手机输入法直接抄。"""


def split_add_flag(text: str) -> tuple[bool, str]:
    """判断是不是 -a/-add/--add，返回 (是否增卡, 规格文本)。"""
    for flag in _ADD_FLAGS:
        if not text.startswith(flag):
            continue
        rest = text[len(flag):]
        if rest and not rest[0].isspace():
            continue
        return True, rest.strip()
    return False, text


def parse_add_spec(text: str) -> dict[str, str]:
    """从规格文本里解析出 zh / en（至少一个）。"""
    spec: dict[str, str] = {}
    for match in _SPEC_PATTERN.finditer(text.translate(_QUOTE_TRANSLATION)):
        key = match.group(1).lower()
        if key in spec:
            continue
        value = next(
            (group for group in match.groups()[1:] if group is not None),
            ""
        ).strip()
        if value:
            spec[key] = value
    return spec


def image_refs(persona_info: PersonaInfo) -> list[str]:
    """取出消息里的图片引用（框架 PersonaInfo.get_images_url）。

    框架版本直接取 msg.data["url"]，收到的 OneBot 消息一定有该字段；
    这里只做一层兜底，避免某条异常消息段把整条命令打断。
    """
    try:
        return persona_info.get_images_url()
    except Exception:
        return []


def invoke_text(cmd: str | tuple[str, ...], *, suffix: str = "") -> str:
    """把 cmd 渲染成用户能照抄的调用串。

    `CommandPackage.cmd` 允许是 `str | tuple[str, ...]`（nonebot 的 on_command
    原生支持多段命令），直接塞进 f-string 会把元组的 repr 甩给用户。
    前缀与分隔符取自框架的 CommandCaller.cmd_prefixs() / delimiters()。
    """
    prefixes = CommandCaller.cmd_prefixs() or {"/"}
    start = "/" if "/" in prefixes else sorted(prefixes)[0]
    if isinstance(cmd, str):
        body = cmd
    else:
        separators = CommandCaller.delimiters() or {"/"}
        separator = "/" if "/" in separators else sorted(separators)[0]
        body = separator.join(cmd)
    return f"{start}{body}{suffix}"


def usage_text(invoke: str) -> str:
    """增卡命令的用法说明；`invoke` 是已渲染好的调用前缀。"""
    return (
        f"用法：{invoke} -a {{\"zh\": \"中文名\", \"en\": \"English\"}}\n"
        "· 中英文至少填一个\n"
        f"· 卡图可以随消息一起发送，或在这之后 {IMAGE_WAIT_TIMEOUT:.0f} 秒内补发\n"
        "· 卡图会转成 PNG 并按 custom_N 自动编号"
    )


@CommandCaller.register
class FindCards(CommandPackage):
    cmd = "FindCards"
    aliases = {
        "FC",
        "fc",
        "findcards",
        "Findcards",
    }
    cmd_type = CmdTypes.CARDS
    """命令分类。用枚举而不是字符串：/cmd_types、/see_cmd、/cmd_type 那几处按 .value 渲染，
    只有枚举成员才能被它们正确显示与反查。"""

    @classmethod
    def documents(cls) -> str:
        """命令说明（运行时渲染，cmd 是 str 或 tuple 都能正确显示）。"""
        invoke = invoke_text(cls.cmd)
        return textwrap.dedent(
            f"""
            按名称检索卡牌卡图，或把新卡图加进卡牌库。

            Usage:
            ```
            {invoke}                                      随机展示一张卡图
            {invoke} [名称]                               按中文名 / 英文名 / card_id 检索
            {invoke} -a {{"zh": "中文名", "en": "English"}}   添加一张卡图（可随消息附图）
            ```
            """
        ).strip()

    async def on_framework_startup(self) -> None:
        """启动时预加载卡牌库，第一条命令就不用等。"""
        if not await LIBRARY.ensure_loaded():
            logger.warning("FindCards | 启动预加载失败，首次调用时会重试。")

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        """入口：先判断是增卡还是检索。"""
        args = persona_info.args_str.strip()
        is_add, spec_text = split_add_flag(args)
        if is_add:
            await self.handle_add(persona_info, send_msg, spec_text)
            return
        await self.handle_query(persona_info, send_msg, args)

    async def handle_query(
            self,
            persona_info: PersonaInfo,
            send_msg: SendMsg,
            query: str
    ) -> None:
        """检索分支：空参数随机抽一张，其余走三级匹配。"""
        if not await LIBRARY.ensure_loaded():
            await send_msg.send_text("卡牌库加载失败，请稍后再试。")
            return
        cards = LIBRARY.cards
        if not cards:
            await send_msg.send_text("卡牌库为空，暂无可展示的卡牌。")
            return
        if not query:
            await self.send_cards(
                persona_info,
                send_msg,
                (random.choice(LIBRARY.cards_with_image() or cards),)
            )
            return
        match = await asyncio.to_thread(
            search,
            LIBRARY.names,
            query,
            cutoff = FUZZY_CUTOFF
        )
        if match is None:
            await send_msg.send_text(f"未找到与「{query}」相符的卡牌。")
            return
        if match.name_count > 1:
            await self.send_candidates(send_msg, match)
            return
        name, group = match.groups[0]
        if persona_info.is_group and len(group) >= SAME_NAME_LIMIT:
            await send_msg.send_text(
                f"「{name}」同名卡牌共 {len(group)} 张，数量过多。\n"
                f"建议转到私聊使用 {invoke_text(self.cmd, suffix = f' {query}')} 获取全部卡图。"
            )
            return
        await self.send_cards(
            persona_info,
            send_msg,
            group,
            name = name,
            kind = match.kind
        )

    async def send_candidates(self, send_msg: SendMsg, match: Match) -> None:
        """命中多个不同名称：只列名称，不发图。"""
        lines = ["检测到多个符合条件的卡："]
        for index, (name, group) in enumerate(match.groups):
            if index >= LIST_LIMIT:
                lines.append(f"…… 以及另外 {match.name_count - LIST_LIMIT} 个名称")
                break
            suffix = f"（{len(group)} 张）" if len(group) > 1 else ""
            lines.append(f"· {name}{suffix}")
        await send_msg.send_text("\n".join(lines))

    async def send_cards(
            self,
            persona_info: PersonaInfo,
            send_msg: SendMsg,
            cards: Sequence[Card],
            *,
            name: str | None = None,
            kind: str = "exact"
    ) -> None:
        """单个名称：名称与卡图放进同一条消息。"""
        lines: list[str] = []
        if kind == "contains":
            lines.append("输入未完全，但找到唯一符合规则")
        elif kind == "fuzzy":
            lines.append("没有完全匹配，最相近的是：")
        lines.append(name or cards[0].display_name)
        images = tuple(card.image for card in cards if card.image is not None)
        if not images:
            lines.append("（未找到对应卡图文件）")
        segments: list[MessageSegment] = [
            MessageSegment.text("\n".join(lines)),
        ]
        segments.extend(MessageSegment.image(image) for image in images)
        message = persona_info.make_message(segments)
        message.reduce()
        await send_msg.send_any(message = message)

    async def handle_add(
            self,
            persona_info: PersonaInfo,
            send_msg: SendMsg,
            spec_text: str
    ) -> None:
        """增卡分支：解析规格 -> 查重 -> 取图 -> 转 PNG -> 写库。"""
        spec = parse_add_spec(spec_text)
        if not spec:
            await send_msg.send_text(usage_text(invoke_text(self.cmd)))
            return
        if not await LIBRARY.ensure_loaded():
            await send_msg.send_text("卡牌库加载失败，请稍后再试。")
            return
        name_zh = spec.get("zh", "")
        name_en = spec.get("en", "")
        clashed = LIBRARY.find_conflict(name_zh, name_en)
        if clashed is not None:
            await send_msg.send_text(
                "已经有同名卡图了，请重新命名\n"
                f"（已存在：{clashed.display_name} / {clashed.card_id}）"
            )
            return
        image = await self.acquire_image(persona_info, send_msg)
        if image is None:
            await send_msg.send_text("你似乎需要再发送一张卡图")
            return
        try:
            card = await LIBRARY.add_card(
                name_zh = name_zh,
                name_en = name_en,
                image = image,
            )
        except ConverterMissing:
            await send_msg.send_text("系统里找不到 ffmpeg，无法把卡图转成 PNG。")
            return
        except ValueError:
            await send_msg.send_text("这张图片无法解码，请换一张卡图。")
            return
        suffix = card.image.suffix if card.image is not None else ""
        await send_msg.send_text(
            f"已保存卡图：{card.name_zh or '（未填）'} / {card.name_en or '（未填）'}"
            f"（{card.card_id}{suffix}）"
        )

    async def acquire_image(
            self,
            persona_info: PersonaInfo,
            send_msg: SendMsg
    ) -> str | None:
        """取一条卡图引用（http(s)/base64/file/本地路径），没有就提示补发。

        这里只取引用、不下载：URL 交给 ffmpeg 直读，省掉「先下载再转码」。
        """
        refs = image_refs(persona_info)
        if not refs:
            await send_msg.send_prompt(
                "请发送要保存的卡图。",
                continue_handler = True
            )
            incoming = await self.wait_for_image(persona_info)
            refs = image_refs(incoming) if incoming is not None else []
        return refs[0] if refs else None

    async def wait_for_image(
            self,
            persona_info: PersonaInfo
    ) -> PersonaInfo | None:
        """等用户补发一条带图消息（最多 IMAGE_WAIT_TIMEOUT 秒）。"""
        listener = await CommandCaller.message_future(
            persona_info.namespace,
            block_propagation = True
        )
        try:
            return await asyncio.wait_for(listener, timeout = IMAGE_WAIT_TIMEOUT)
        except asyncio.TimeoutError:
            return None
        finally:
            await CommandCaller.cancel_wait_message_listener(listener.id)

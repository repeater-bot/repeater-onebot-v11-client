"""检索逻辑：完全匹配 -> 包含匹配 -> 模糊匹配。

这里的函数都是纯 CPU 计算，调用方负责放进 asyncio.to_thread，
避免 rapidfuzz 的比较过程阻塞事件循环。

模糊匹配用框架 assist.fuzzy.FuzzyMatch.most_similar（内部就是 rapidfuzz 的
process.extractOne，scorer 默认 fuzz.WRatio）；低于阈值时它返回
(None, None, None)，不需要自己判断空列表。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal, Sequence

from ...assist import FuzzyMatch

from .aliases import ALIASES
from .models import Card, normalize

MatchKind = Literal["exact", "contains", "fuzzy"]
"""匹配来源：完全命中 / 输入未完全 / 模糊最相近。"""

Group = tuple[str, tuple[Card, ...]]
"""同名卡牌分组：(展示名, 该名下的卡牌)。"""


@dataclass(frozen = True, slots = True)
class NameRef:
    """一个归一化后的可检索名称，以及它所属的卡牌。"""

    key: str
    card: Card


@dataclass(frozen = True, slots = True)
class Match:
    """一次检索的结果。"""

    kind: MatchKind
    groups: tuple[Group, ...]

    @property
    def name_count(self) -> int:
        """命中了多少个不同的名称。"""
        return len(self.groups)

    @property
    def cards(self) -> tuple[Card, ...]:
        """命中的全部卡牌。"""
        return tuple(card for _name, cards in self.groups for card in cards)


def build_names(cards: Sequence[Card]) -> tuple[NameRef, ...]:
    """构造可检索名称表：中文名、英文名、card_id、别名各算一条。"""
    refs: list[NameRef] = []
    for card in cards:
        for raw in (
            card.name_zh,
            card.name_en,
            card.card_id,
            *ALIASES.get(card.card_id, ()),
        ):
            key = normalize(raw)
            if key:
                refs.append(NameRef(key = key, card = card))
    return tuple(refs)


def group_by_display(cards: Iterable[Card]) -> tuple[Group, ...]:
    """按展示名分组，保持传入顺序，并按 card_id 去重。"""
    order: list[str] = []
    bucket: dict[str, list[Card]] = {}
    seen: set[str] = set()
    for card in cards:
        if card.card_id in seen:
            continue
        seen.add(card.card_id)
        name = card.display_name
        if name not in bucket:
            order.append(name)
            bucket[name] = []
        bucket[name].append(card)
    return tuple((name, tuple(bucket[name])) for name in order)


def fuzzy_cutoff(target: str, cutoff: float) -> float:
    """短名称放宽阈值：4~5 个字只差一个字时，WRatio 只有 75 上下。

    长名称仍以传入的 cutoff 为上限，短名称最多宽到约「允许一个字不同」，
    下限 60，避免两三个字的输入把不相干的卡也捞出来。
    """
    length = max(len(target), 2)
    allowed = 100.0 - 100.0 / length - 3.0
    return max(60.0, min(cutoff, allowed))


def search(
        names: Sequence[NameRef],
        query: str,
        *,
        cutoff: float
) -> Match | None:
    """按 完全 -> 包含 -> 模糊 三级检索，全部落空返回 None。"""
    target = normalize(query)
    if not target or not names:
        return None

    exact = [ref.card for ref in names if ref.key == target]
    if exact:
        return Match("exact", group_by_display(exact))

    partial = [ref.card for ref in names if target in ref.key]
    if partial:
        return Match("contains", group_by_display(partial))

    return fuzzy(names, target, cutoff = cutoff)


def fuzzy(
        names: Sequence[NameRef],
        target: str,
        *,
        cutoff: float
) -> Match | None:
    """取最相近的一个名称，并带出该名称下的全部卡牌。

    这里不用 FuzzyMatch.most_similar：它内部是 `target, score, index =
    process.extractOne(...)`，而 rapidfuzz 在 score_cutoff 过滤掉全部候选时
    返回的是裸 None，解包直接抛 TypeError（框架的类型标注写的是
    (None, None, None)，与实际不符）。most_similar_n 走 process.extract，
    无命中时返回空列表，可以安全判定。
    """
    results = FuzzyMatch(
        [ref.key for ref in names]
    ).most_similar_n(
        target,
        limit = 1,
        score_cutoff = fuzzy_cutoff(target, cutoff)
    )
    if not results:
        return None
    key = names[results[0][2]].key
    siblings = [ref.card for ref in names if ref.key == key]
    return Match("fuzzy", group_by_display(siblings))

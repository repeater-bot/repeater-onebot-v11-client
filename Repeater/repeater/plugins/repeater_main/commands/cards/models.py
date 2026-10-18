"""卡牌数据模型与名称归一化。"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from pathlib import Path


def normalize(text: str) -> str:
    """归一化名称：NFKC 折叠、去掉全部空白、大小写折叠。

    卡牌中文名里有大量带空格的写法（如「近卫步兵第 1 团」），
    归一化后空白不参与比较，用户怎么打都能命中；
    全角/半角与大小写差异一并抹平。
    """
    if not text:
        return ""
    return "".join(unicodedata.normalize("NFKC", text).split()).casefold()


@dataclass(frozen = True, slots = True)
class Card:
    """一张卡牌：索引里的名称 + 磁盘上的卡图。"""

    card_id: str
    """卡牌标识，同时也是卡图文件名（不含后缀）。"""

    name_zh: str
    """中文名，索引里没有时为空串。"""

    name_en: str
    """英文名，索引里没有时为空串。"""

    image: Path | None
    """卡图路径；磁盘上没有对应文件时为 None。"""

    @property
    def display_name(self) -> str:
        """展示名：中文名 > 英文名 > card_id。"""
        return self.name_zh or self.name_en or self.card_id

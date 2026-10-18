"""玩家提供的译名备选写法。

原始需求里，没有官方英文名的卡由用户手动给了译名，其中若干卡给了多个候选写法
（「帝国高级研发 或 高级帝国研发」这种）。索引里保留的是与官方卡图一致的那个写法，
用户给的其余候选登记在这里，**只参与检索、不写入索引**：

- 命中别名时，回复里显示的仍是卡面名称（Card.display_name）；
- 只有一种写法的卡不需要登记，索引本身已经能搜到。

要加新别名，往 ALIASES 里加一行即可（key 必须是索引里的 card_id）。
"""

from __future__ import annotations

from typing import Final

ALIASES: Final[dict[str, tuple[str, ...]]] = {
    "advanced_imperial_rd": ("高级帝国研发",),
    "advanced_soviet_research": ("高级苏联研发",),
    "aerosani": ("气动雪橇",),
    "expanded_imperial_rd": ("帝国扩展研发", "扩展帝国研发", "拓展帝国研发"),
    "expanded_soviet_research": ("苏联扩展研发", "扩展苏联研发", "拓展苏联研发"),
    "long_lance": ("氧气鱼雷",),
    "raaf_lightning_f4": ("RAAF闪电F-4",),
    "ruffians": ("恶汉团",),
}

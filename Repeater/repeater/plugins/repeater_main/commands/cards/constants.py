"""卡牌命令的全部固定参数。

数据路径一律写成相对框架 STORAGE_BASE_PATH（.env 里的 ../storage）的相对名，
交给框架 storage 自己拼接，因此：

- 换机器、换盘、换 STORAGE_BASE_PATH 都不用改这里；
- 不依赖 __file__ 之外的任何推断，也不随本模块的位置漂移。
"""

from __future__ import annotations

from typing import Final

INDEX_NAME: Final[str] = "card_names.jsonl"
"""卡牌名称索引，相对 STORAGE_BASE_PATH。JSONL：一行一张卡。"""

IMAGES_NAME: Final[str] = "images"
"""卡图目录，相对 STORAGE_BASE_PATH；文件名即 card_id。"""

INDEX_KEY_ID: Final[str] = "card_id"
"""JSONL 记录里卡牌标识的键名。"""

INDEX_KEY_ZH: Final[str] = "zh"
"""JSONL 记录里中文名的键名。"""

INDEX_KEY_EN: Final[str] = "en"
"""JSONL 记录里英文名的键名。"""

IMAGE_SUFFIX: Final[str] = ".png"
"""允许被纳入卡牌库的卡图后缀。"""

SAVED_IMAGE_SUFFIX: Final[str] = ".png"
"""新增卡图一律转存为 PNG。"""

CUSTOM_ID_PREFIX: Final[str] = "custom_"
"""新增卡图的自动编号前缀（custom_1、custom_2 ……）。"""

LIST_LIMIT: Final[int] = 60
"""命中多个名称时最多列举的行数。"""

SAME_NAME_LIMIT: Final[int] = 3
"""同名卡牌达到该数量时，群聊改为提示转私聊。"""

FUZZY_CUTOFF: Final[float] = 78.0
"""模糊匹配的最低分数（rapidfuzz WRatio，0-100）。"""

IMAGE_WAIT_TIMEOUT: Final[float] = 60.0
"""添加卡图时等待用户补发图片的秒数。"""

IMAGE_DOWNLOAD_TIMEOUT: Final[float] = 30.0
"""ffmpeg 读网络图片时的读写超时（秒）。"""

FFMPEG_BINARY: Final[str] = "ffmpeg"
"""把任意图片转成 PNG 用的可执行文件（取自 PATH）。"""

FFMPEG_USER_AGENT: Final[str] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
"""ffmpeg 读 URL 时携带的 User-Agent；QQ 图床对空 UA 有时会拒绝。"""

IMAGE_CONVERT_TIMEOUT: Final[float] = 30.0
"""单次图片转换（含网络读取）的超时秒数。"""

PNG_MAGIC: Final[bytes] = b"\x89PNG\r\n\x1a\n"
"""PNG 文件头；已经是 PNG 的图片直接原样落盘，不调 ffmpeg。"""

"""卡牌库：索引加载、卡图扫描、新增卡图。

- 索引是 JSONL（一行一张卡），追加新卡用框架的 save_jsonl(append = True)，
  不需要读全量再重写，也就没有「写一半把索引写坏」的窗口；
- 读取用 load_line_stream 逐行解析，单行坏掉只跳过并告警，不拖垮整库；
- 耗时操作（目录扫描、图片解码、PNG 编码）全部丢进 asyncio.to_thread。
"""

from __future__ import annotations

import asyncio
import base64
import shutil
import tempfile
import urllib.parse
import urllib.request
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Final

import orjson

from ...logger import logger
from ...storage import async_binary_storage, async_json_storage

from .constants import (
    CUSTOM_ID_PREFIX,
    FFMPEG_BINARY,
    FFMPEG_USER_AGENT,
    IMAGE_CONVERT_TIMEOUT,
    IMAGE_SUFFIX,
    IMAGES_NAME,
    INDEX_KEY_EN,
    INDEX_KEY_ID,
    INDEX_KEY_ZH,
    INDEX_NAME,
    PNG_MAGIC,
    SAVED_IMAGE_SUFFIX,
)
from .matching import NameRef, build_names
from .models import Card, normalize


class ConverterMissing(RuntimeError):
    """系统里找不到 ffmpeg，无法把图片转成 PNG。"""


def scan_images(directory: Path) -> dict[str, Path]:
    """扫描卡图目录，返回 card_id -> 卡图路径（阻塞，须在 to_thread 内调用）。"""
    found: dict[str, Path] = {}
    try:
        entries = [
            entry
            for entry in directory.iterdir()
            if entry.suffix.lower() == IMAGE_SUFFIX
        ]
    except OSError:
        return found
    for entry in sorted(entries, key = lambda item: item.name):
        try:
            if not entry.is_file() or not entry.stem:
                continue
        except OSError:
            continue
        found.setdefault(entry.stem, entry)
    return found


def build_cards(
        records: list[Mapping[str, Any]],
        images: Mapping[str, Path]
) -> tuple[Card, ...]:
    """合并索引与卡图，得到卡牌元组（阻塞，须在 to_thread 内调用）。"""
    cards: list[Card] = []
    seen: set[str] = set()
    for record in records:
        card_id = str(record.get(INDEX_KEY_ID) or "").strip()
        if not card_id or card_id in seen:
            continue
        seen.add(card_id)
        cards.append(
            Card(
                card_id = card_id,
                name_zh = str(record.get(INDEX_KEY_ZH) or "").strip(),
                name_en = str(record.get(INDEX_KEY_EN) or "").strip(),
                image = images.get(card_id),
            )
        )
    for card_id, image in images.items():
        if card_id in seen:
            continue
        seen.add(card_id)
        cards.append(Card(card_id, "", "", image))
    return tuple(cards)


async def to_png_bytes(source: str | bytes) -> bytes:
    """把图片引用或图片字节转成 PNG 字节。

    - `http(s)://` 直接交给 ffmpeg 读（ffmpeg 自带 http 协议），**不预先下载**；
    - `base64://` / `file://` / 本地路径先取成字节，再走字节分支；
    - 已经是 PNG 的字节原样返回，不启动子进程。

    转换失败或超时抛 ValueError；ffmpeg 缺失抛 ConverterMissing。
    """
    if isinstance(source, bytes):
        data = source
    elif source.startswith(("http://", "https://")):
        return await _convert(source, is_url = True)
    elif source.startswith("base64://"):
        return await to_png_bytes(base64.b64decode(source[len("base64://"):]))
    elif source.startswith("file://"):
        data = await asyncio.to_thread(_file_url_to_path(source).read_bytes)
    else:
        data = await asyncio.to_thread(Path(source).read_bytes)

    if data.startswith(PNG_MAGIC):
        return data
    return await _convert(data, is_url = False)


def _file_url_to_path(reference: str) -> Path:
    """把 file:// 引用还原成本地路径。"""
    parsed = urllib.parse.urlparse(reference)
    return Path(urllib.request.url2pathname(urllib.parse.unquote(parsed.path)))


async def _convert(payload: str | bytes, *, is_url: bool) -> bytes:
    """调 ffmpeg 把一张图转成 PNG（异步子进程，不占事件循环）。"""
    binary = await asyncio.to_thread(shutil.which, FFMPEG_BINARY)
    if binary is None:
        raise ConverterMissing(f"系统中找不到 {FFMPEG_BINARY}")

    with tempfile.TemporaryDirectory(prefix = "cards_png_") as directory:
        root = Path(directory)
        if is_url:
            reference = str(payload)
        else:
            source = root / "source"
            await asyncio.to_thread(source.write_bytes, payload)
            reference = str(source)
        target = root / "target.png"

        arguments = [binary, "-y", "-hide_banner", "-loglevel", "error"]
        if is_url:
            arguments += [
                "-user_agent", FFMPEG_USER_AGENT,
                "-rw_timeout", str(int(IMAGE_CONVERT_TIMEOUT * 1_000_000)),
            ]
        arguments += ["-i", reference, "-frames:v", "1", "-c:v", "png", str(target)]

        process = await asyncio.create_subprocess_exec(
            *arguments,
            stdout = asyncio.subprocess.DEVNULL,
            stderr = asyncio.subprocess.PIPE,
        )
        try:
            _out, err = await asyncio.wait_for(
                process.communicate(),
                timeout = IMAGE_CONVERT_TIMEOUT
            )
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
            raise ValueError("图片转换超时") from None
        if process.returncode != 0:
            detail = err.decode("utf-8", "ignore").strip()[:200]
            raise ValueError(f"ffmpeg 转换失败: {detail}")
        png = await asyncio.to_thread(target.read_bytes)

    if not png.startswith(PNG_MAGIC):
        raise ValueError("ffmpeg 没有产出 PNG")
    return png


class CardLibrary:
    """卡牌库（进程内单例）。

    第一次使用时加载，之后常驻内存；新增卡图会同步更新内存与索引文件。
    """

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._cards: tuple[Card, ...] = ()
        self._names: tuple[NameRef, ...] = ()
        self._loaded = False

    @property
    def cards(self) -> tuple[Card, ...]:
        """全部卡牌。"""
        return self._cards

    @property
    def names(self) -> tuple[NameRef, ...]:
        """全部可检索名称（交给 matching.search）。"""
        return self._names

    @property
    def loaded(self) -> bool:
        """索引是否已加载。"""
        return self._loaded

    def cards_with_image(self) -> tuple[Card, ...]:
        """只保留卡图存在的卡牌。"""
        return tuple(card for card in self._cards if card.image is not None)

    def find_conflict(self, name_zh: str, name_en: str) -> Card | None:
        """查找重名卡牌（中文名或英文名任一相同即算冲突）。"""
        target_zh = normalize(name_zh)
        target_en = normalize(name_en)
        if not target_zh and not target_en:
            return None
        for ref in self._names:
            if target_zh and ref.key == target_zh:
                return ref.card
            if target_en and ref.key == target_en:
                return ref.card
        return None

    async def ensure_loaded(self) -> bool:
        """确保索引已加载，返回是否可用（并发调用只会真正加载一次）。"""
        if self._loaded:
            return True
        async with self._lock:
            if self._loaded:
                return True
            try:
                await self._load()
            except Exception as error:
                logger.exception(
                    "FindCards | 卡牌库加载失败: {error}",
                    error = repr(error)
                )
                return False
        return True

    async def _load(self) -> None:
        records = await self._read_index()
        images = await asyncio.to_thread(
            scan_images,
            async_binary_storage.path(IMAGES_NAME)
        )
        cards = await asyncio.to_thread(build_cards, records, images)
        self._cards = cards
        self._names = build_names(cards)
        self._loaded = True
        logger.info(
            "FindCards | 卡牌库加载完成: {cards} 张卡牌 / {images} 张卡图 / {names} 个可检索名称",
            cards = len(cards),
            images = len(images),
            names = len(self._names)
        )

    async def _read_index(self) -> list[Mapping[str, Any]]:
        """逐行读取 JSONL 索引；坏行只跳过并计数，不中断加载。"""
        records: list[Mapping[str, Any]] = []
        broken = 0
        async for line in async_json_storage.load_line_stream(INDEX_NAME):
            raw = line.strip()
            if not raw:
                continue
            try:
                record = orjson.loads(raw)
            except Exception:
                broken += 1
                continue
            if isinstance(record, Mapping) and record.get(INDEX_KEY_ID):
                records.append(record)
            else:
                broken += 1
        if broken:
            logger.warning(
                "FindCards | 索引中有 {count} 行无法解析，已跳过",
                count = broken
            )
        return records

    async def add_card(
            self,
            *,
            name_zh: str,
            name_en: str,
            image: str | bytes
    ) -> Card:
        """保存一张新卡图并登记名称，返回新的卡牌。

        `image` 可以是 http(s) URL、base64://、file://、本地路径或原始字节；
        URL 交给 ffmpeg 直读，不预先下载。

        整段流程持锁，避免两个并发请求分到同一个 custom_N 编号。
        先落图、再追加索引；索引写失败就把刚存的图删掉，不留孤儿文件。
        """
        if not self._loaded:
            raise RuntimeError("卡牌库尚未加载")
        async with self._lock:
            png = await to_png_bytes(image)
            card_id = self._allocate_id()
            relative = f"{IMAGES_NAME}/{card_id}{SAVED_IMAGE_SUFFIX}"
            await async_binary_storage.save(relative, png)
            try:
                await async_json_storage.save_jsonl(
                    INDEX_NAME,
                    [
                        {
                            INDEX_KEY_ID: card_id,
                            INDEX_KEY_ZH: name_zh,
                            INDEX_KEY_EN: name_en,
                        }
                    ],
                    append = True
                )
            except Exception:
                async_binary_storage.remove(relative)
                raise
            card = Card(
                card_id = card_id,
                name_zh = name_zh,
                name_en = name_en,
                image = async_binary_storage.path(relative),
            )
            self._cards = (*self._cards, card)
            self._names = (*self._names, *build_names((card,)))
            logger.info(
                "FindCards | 已保存卡图 {card_id} / {size} bytes",
                card_id = card_id,
                size = len(png)
            )
            return card

    def _allocate_id(self) -> str:
        """生成下一个未被占用的自定义编号。"""
        used = {card.card_id for card in self._cards}
        number = 1
        while f"{CUSTOM_ID_PREFIX}{number}" in used:
            number += 1
        return f"{CUSTOM_ID_PREFIX}{number}"


LIBRARY: Final[CardLibrary] = CardLibrary()
"""本命令共用的卡牌库实例。"""

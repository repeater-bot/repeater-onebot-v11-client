"""上下文正则检索：模式校验、扫描统计、分支编排与报告渲染。

searchContext 与 matchContext 只差一个锚定方式，其余全部共用这里：

- 纯 CPU 部分（compile_pattern / scan_texts）不做 IO、也不 await，调用方负责
  放进 asyncio.to_thread，避免正则扫描阻塞事件循环（与 commands/cards/matching.py
  的约定一致）。
- 编排部分（scan_branches / execute）负责取分支、并发拉取与汇报。

用 regex 而不是标准库 re，只为了 timeout 参数：用户传入的正则可能触发指数级
回溯，re 没有任何手段中断，regex 能给单次匹配一个硬上限。
注意 regex 超时抛的是内置 TimeoutError，模块里没有 regex.TimeoutError。
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Sequence

import regex

from ....assist import PersonaInfo, SendMsg
from ....client_configs import storage_configs
from ....clients import ContextClient


@dataclass(frozen = True, slots = True)
class ScanResult:
    """一次扫描的统计结果。"""

    records_hit: int
    """命中至少一次的记录条数，命中率的分子。"""

    records_total: int
    """参与扫描的记录条数，命中率的分母。"""

    occurrences: int
    """命中次数。search 模式是匹配出现的次数，match 模式与命中条数相同（每条至多一次）。"""

    @property
    def ratio(self) -> float:
        """命中率，没有记录时为 0.0。"""
        return self.records_hit / self.records_total if self.records_total else 0.0

    def merge(self, other: ScanResult) -> ScanResult:
        """累加另一份统计。"""
        return ScanResult(
            records_hit = self.records_hit + other.records_hit,
            records_total = self.records_total + other.records_total,
            occurrences = self.occurrences + other.occurrences
        )


def compile_pattern(raw: str) -> regex.Pattern:
    """校验并编译用户传入的正则。

    :param raw: 命令参数的原文
    :return: 编译好的正则
    :raises ValueError: 模式为空、过长、语法错误，或能匹配空字符串
    """
    configs = storage_configs.context_search
    text = raw.strip()
    if not text:
        raise ValueError("检索模式不能为空")
    if len(text) > configs.max_pattern_chars:
        raise ValueError(f"检索模式过长，上限 {configs.max_pattern_chars} 字符")

    try:
        pattern = regex.compile(text)
    except regex.error as exc:
        raise ValueError(f"正则语法错误：{exc}") from exc

    if pattern.search("", timeout = configs.match_timeout) is not None:
        raise ValueError("检索模式能匹配空字符串，命中率会恒为 100%，请加上限定（如 .+ / \\S+）")

    return pattern


def scan_texts(
        texts: Sequence[str],
        pattern: regex.Pattern,
        *,
        anchored: bool
    ) -> ScanResult:
    """扫描一批完整字符串，统计命中条数与出现次数。

    不切行：行首行尾由用户自己在模式里用 (?m)^ 之类控制。

    :param texts: 待扫描的字符串
    :param pattern: compile_pattern 的结果
    :param anchored: True 用 match（从整串开头），False 用 search（任意位置）
    :raises TimeoutError: 单次匹配超过 storage_configs.context_search.match_timeout
    """
    timeout = storage_configs.context_search.match_timeout
    records_hit = 0
    occurrences = 0

    if anchored:
        # match 锚在整串开头，每条最多命中一次，出现次数即命中条数
        for text in texts:
            if pattern.match(text, timeout = timeout) is not None:
                records_hit += 1
        occurrences = records_hit
    else:
        # findall 一趟同时给出命中条数与出现次数，省掉第二次扫描
        for text in texts:
            hits = len(pattern.findall(text, timeout = timeout))
            if hits:
                records_hit += 1
                occurrences += hits

    return ScanResult(
        records_hit = records_hit,
        records_total = len(texts),
        occurrences = occurrences
    )


class ScanError(Exception):
    """检索过程中不可恢复的错误。"""

    def __init__(self, message: str, response: Any = None):
        super().__init__(message)
        self.response = response


@dataclass(frozen = True, slots = True)
class BranchScan:
    """单个分支的扫描结果。"""

    branch_id: str
    result: ScanResult


@dataclass(frozen = True, slots = True)
class ScanReport:
    """一次完整检索的结果。"""

    pattern: str
    anchored: bool
    scans: tuple[BranchScan, ...]
    failed: tuple[str, ...]
    """读取或扫描失败的分支，不进分子分母。"""

    skipped: int
    """空分支数（没有可统计的记录）。"""

    @property
    def total(self) -> ScanResult:
        """所有参与统计的分支的合计。"""
        total = ScanResult(0, 0, 0)
        for scan in self.scans:
            total = total.merge(scan.result)
        return total

    def ranked(self) -> tuple[BranchScan, ...]:
        """按命中率降序排列，同率时命中条数多的在前。"""
        return tuple(
            sorted(
                self.scans,
                key = lambda scan: (scan.result.ratio, scan.result.records_hit),
                reverse = True
            )
        )


async def scan_branches(
        client: ContextClient,
        pattern: regex.Pattern,
        *,
        anchored: bool
    ) -> ScanReport:
    """拉取全部上下文分支并统计。

    同一 ContextClient 可并发使用：get_context_contents 无副作用，不像
    change_branch 那样改服务端的活动分支。

    :param client: ContextClient 实例
    :param pattern: compile_pattern 的结果
    :param anchored: True 用 match，False 用 search
    :raises ScanError: 拿不到分支列表，或某个模式触发匹配超时
    """
    branch_response = await client.get_branch_list()
    if not branch_response:
        raise ScanError("获取分支列表失败", branch_response)

    branches = branch_response.json()
    if not isinstance(branches, list) or not branches:
        raise ScanError("没有可检索的分支")

    semaphore = asyncio.Semaphore(storage_configs.context_search.branch_concurrency)

    async def scan_one(branch_id: str) -> BranchScan:
        async with semaphore:
            response = await client.get_context_contents(branch_id)
            if not response:
                raise LookupError(f"HTTP {response.code}")
            contents = response.get_data() or []
        result = await asyncio.to_thread(
            scan_texts,
            contents,
            pattern,
            anchored = anchored
        )
        return BranchScan(branch_id, result)

    scanned = await asyncio.gather(
        *(scan_one(branch_id) for branch_id in branches),
        return_exceptions = True
    )

    scans: list[BranchScan] = []
    failed: list[str] = []
    skipped = 0

    for branch_id, item in zip(branches, scanned):
        if isinstance(item, TimeoutError):
            timeout = storage_configs.context_search.match_timeout
            raise ScanError(
                f"检索模式在 {timeout:g} 秒内没跑完，疑似指数级回溯，已中止"
            )
        if isinstance(item, asyncio.CancelledError):
            # 命令被取消时不能当成普通分支失败，要让取消继续向上传播
            raise item
        if isinstance(item, BaseException):
            failed.append(branch_id)
            continue
        if item.result.records_total <= 0:
            skipped += 1
            continue
        scans.append(item)

    return ScanReport(
        pattern = pattern.pattern,
        anchored = anchored,
        scans = tuple(scans),
        failed = tuple(failed),
        skipped = skipped
    )


def format_report(report: ScanReport) -> str:
    """把统计结果渲染成给用户看的文本。"""
    mode = "match（从整串开头）" if report.anchored else "search（任意位置）"
    lines: list[str] = [
        f"模式：{report.pattern}",
        f"方式：{mode}",
        ""
    ]

    ranked = report.ranked()
    matched = tuple(scan for scan in ranked if scan.result.records_hit > 0)
    shown = matched[:storage_configs.context_search.max_reported_branches]

    if not matched:
        lines.append("（没有任何分支命中）")
    for scan in shown:
        result = scan.result
        lines.append(
            f"· {scan.branch_id}  {result.records_hit}/{result.records_total}"
            f"  {result.ratio:.1%}  共 {result.occurrences} 次"
        )
    if len(matched) > len(shown):
        lines.append(f"… 另有 {len(matched) - len(shown)} 个命中分支未列出")

    total = report.total
    lines.append("")
    lines.append(
        f"整体：{total.records_hit}/{total.records_total} = {total.ratio:.1%}"
        f"  共 {total.occurrences} 次"
    )

    if report.skipped:
        lines.append(f"跳过：{report.skipped} 个空分支")
    if report.failed:
        names = "、".join(report.failed[:5])
        more = f" 等 {len(report.failed)} 个" if len(report.failed) > 5 else ""
        lines.append(f"失败：{names}{more}，未计入统计")

    return "\n".join(lines)


async def execute(
        persona_info: PersonaInfo,
        send_msg: SendMsg,
        *,
        anchored: bool
    ) -> None:
    """两个命令共用的流程：取参数 -> 编译 -> 扫描 -> 汇报。

    :param persona_info: 当前会话信息
    :param send_msg: 消息发送器
    :param anchored: True 用 match，False 用 search
    """
    try:
        pattern = compile_pattern(persona_info.args_str)
    except ValueError as exc:
        await send_msg.send_error(str(exc))
        return

    user_configs = await persona_info.get_user_configs()
    context_client = ContextClient(persona_info, user_configs)

    try:
        report = await scan_branches(context_client, pattern, anchored = anchored)
    except ScanError as exc:
        if exc.response is None:
            await send_msg.send_error(str(exc))
        else:
            await send_msg.send_response_check_code(exc.response, str(exc))
        return

    await send_msg.send_check_length_prompt(
        format_report(report),
        code_block = True
    )

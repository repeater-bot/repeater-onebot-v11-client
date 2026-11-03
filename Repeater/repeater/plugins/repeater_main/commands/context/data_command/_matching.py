"""Context regex search: pattern validation, scanning, aggregation and reporting.

searchContext and matchContext differ only in how they anchor; everything else is
shared here.

- The pure CPU parts (compile_pattern / scan_texts) do no IO and never await. Callers
  are responsible for running them in asyncio.to_thread so regex scanning cannot block
  the event loop (same convention as commands/cards/matching.py).
- The orchestration parts (scan_branches / execute) handle branch listing, concurrent
  fetching and reporting.

The regex module is used instead of the stdlib re purely for its timeout argument: a
user supplied pattern may trigger exponential backtracking, which re cannot interrupt,
while regex can bound a single match. Note that regex raises the builtin TimeoutError
on timeout; the module has no regex.TimeoutError attribute.
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
    """Statistics for a single scan."""

    records_hit: int
    """Number of records matched at least once, the numerator of the hit rate."""

    records_total: int
    """Number of records scanned, the denominator of the hit rate."""

    occurrences: int
    """Number of matches. In search mode this is the match count, in match mode it
    equals records_hit because anchoring allows at most one hit per record."""

    @property
    def ratio(self) -> float:
        """Hit rate, 0.0 when nothing was scanned."""
        return self.records_hit / self.records_total if self.records_total else 0.0

    def merge(self, other: ScanResult) -> ScanResult:
        """Return a result with another one added in."""
        return ScanResult(
            records_hit = self.records_hit + other.records_hit,
            records_total = self.records_total + other.records_total,
            occurrences = self.occurrences + other.occurrences
        )


def compile_pattern(raw: str) -> regex.Pattern:
    """Validate and compile a user supplied regex.

    :param raw: the raw command argument
    :return: the compiled pattern
    :raises ValueError: the pattern is empty, too long, syntactically invalid,
        or matches the empty string
    """
    configs = storage_configs.context_search
    text = raw.strip()
    if not text:
        raise ValueError("Pattern must not be empty")
    if len(text) > configs.max_pattern_chars:
        raise ValueError(f"Pattern too long, limit is {configs.max_pattern_chars} characters")

    try:
        pattern = regex.compile(text)
    except regex.error as exc:
        raise ValueError(f"Invalid regex: {exc}") from exc

    if pattern.search("", timeout = configs.match_timeout) is not None:
        raise ValueError(
            "Pattern matches the empty string, which would make every hit rate 100%; "
            "add a constraint such as .+ or \\S+"
        )

    return pattern


def scan_texts(
        texts: Sequence[str],
        pattern: regex.Pattern,
        *,
        anchored: bool
    ) -> ScanResult:
    """Scan a batch of whole strings and count hits and matches.

    Lines are not split: line anchoring is up to the user via (?m)^ and friends.

    :param texts: the strings to scan
    :param pattern: the result of compile_pattern
    :param anchored: True uses match (from the start of the content),
        False uses search (anywhere in the content)
    :raises TimeoutError: a single match exceeded
        storage_configs.context_search.match_timeout
    """
    timeout = storage_configs.context_search.match_timeout
    records_hit = 0
    occurrences = 0

    if anchored:
        # Anchored at the start of the content, so each record hits at most once
        # and the number of occurrences equals the number of hit records.
        for text in texts:
            if pattern.match(text, timeout = timeout) is not None:
                records_hit += 1
        occurrences = records_hit
    else:
        # A single findall pass yields both the hit count and the match count,
        # which saves a second scan.
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
    """Unrecoverable error during a scan."""

    def __init__(self, message: str, response: Any = None):
        super().__init__(message)
        self.response = response


@dataclass(frozen = True, slots = True)
class BranchScan:
    """Scan result of a single branch."""

    branch_id: str
    result: ScanResult


@dataclass(frozen = True, slots = True)
class ScanReport:
    """Result of a full scan."""

    pattern: str
    anchored: bool
    scans: tuple[BranchScan, ...]
    failed: tuple[str, ...]
    """Branches that could not be loaded or scanned, excluded from both counters."""

    skipped: int
    """Number of empty branches with nothing to scan."""

    @property
    def total(self) -> ScanResult:
        """Combined result over every branch that took part."""
        total = ScanResult(0, 0, 0)
        for scan in self.scans:
            total = total.merge(scan.result)
        return total

    def ranked(self) -> tuple[BranchScan, ...]:
        """Sort by hit rate descending, ties broken by the higher hit count."""
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
    """Fetch every context branch and scan it.

    The same ContextClient can be used concurrently: get_context_contents has no side
    effects, unlike change_branch which mutates the active branch on the server.

    :param client: a ContextClient instance
    :param pattern: the result of compile_pattern
    :param anchored: True uses match, False uses search
    :raises ScanError: the branch list is unavailable, or a match timed out
    """
    branch_response = await client.get_branch_list()
    if not branch_response:
        raise ScanError("Failed to get branch list", branch_response)

    branches = branch_response.json()
    if not isinstance(branches, list) or not branches:
        raise ScanError("No branches to search")

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
                f"Pattern did not finish within {timeout:g}s, "
                "possible catastrophic backtracking, aborted"
            )
        if isinstance(item, asyncio.CancelledError):
            # A cancelled command must not be recorded as a branch failure.
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


def _count(count: int, singular: str, plural: str) -> str:
    """Render a count together with the matching noun form."""
    return f"{count} {singular if count == 1 else plural}"


def format_report(report: ScanReport) -> str:
    """Render the scan result as text for the user."""
    if report.anchored:
        mode = "match (anchored at the start of the content)"
    else:
        mode = "search (anywhere in the content)"

    lines: list[str] = [
        f"Pattern: {report.pattern}",
        f"Mode: {mode}",
        ""
    ]

    ranked = report.ranked()
    matched = tuple(scan for scan in ranked if scan.result.records_hit > 0)
    shown = matched[:storage_configs.context_search.max_reported_branches]

    if not matched:
        lines.append("(no branch matched)")
    for scan in shown:
        result = scan.result
        lines.append(
            f"- {scan.branch_id}: {result.records_hit}/{result.records_total}"
            f" ({result.ratio:.1%}), {_count(result.occurrences, 'match', 'matches')}"
        )
    if len(matched) > len(shown):
        more = _count(len(matched) - len(shown), "matching branch", "matching branches")
        lines.append(f"... and {more} not listed")

    total = report.total
    lines.append("")
    lines.append(
        f"Total: {total.records_hit}/{total.records_total}"
        f" = {total.ratio:.1%}, {_count(total.occurrences, 'match', 'matches')}"
    )

    if report.skipped:
        lines.append(f"Skipped: {_count(report.skipped, 'empty branch', 'empty branches')}")
    if report.failed:
        names = ", ".join(report.failed[:5])
        more = f" and {len(report.failed) - 5} more" if len(report.failed) > 5 else ""
        lines.append(f"Failed: {names}{more} (excluded from totals)")

    return "\n".join(lines)


async def execute(
        persona_info: PersonaInfo,
        send_msg: SendMsg,
        *,
        anchored: bool
    ) -> None:
    """Shared flow of both commands: read args, compile, scan, report.

    :param persona_info: the current session info
    :param send_msg: the message sender
    :param anchored: True uses match, False uses search
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

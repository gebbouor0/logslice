"""Rank log lines by frequency of a field or pattern."""
from __future__ import annotations
from dataclasses import dataclass, field
from collections import Counter
from typing import List, Optional
from logslice.parser import LogLine
import re


@dataclass
class RankEntry:
    value: str
    count: int
    lines: List[LogLine] = field(default_factory=list)


@dataclass
class RankResult:
    entries: List[RankEntry] = field(default_factory=list)

    def top(self, n: int = 10) -> List[RankEntry]:
        return sorted(self.entries, key=lambda e: e.count, reverse=True)[:n]

    def bottom(self, n: int = 10) -> List[RankEntry]:
        return sorted(self.entries, key=lambda e: e.count)[:n]

    def __len__(self) -> int:
        return len(self.entries)


def _extract_value(line: LogLine, pattern: str) -> Optional[str]:
    m = re.search(pattern, line.message)
    return m.group(0) if m else None


def rank_by_pattern(lines: List[LogLine], pattern: str) -> RankResult:
    buckets: dict[str, RankEntry] = {}
    for line in lines:
        val = _extract_value(line, pattern)
        if val is None:
            continue
        if val not in buckets:
            buckets[val] = RankEntry(value=val, count=0)
        buckets[val].count += 1
        buckets[val].lines.append(line)
    return RankResult(entries=list(buckets.values()))


def rank_by_field(lines: List[LogLine], field_name: str) -> RankResult:
    buckets: dict[str, RankEntry] = {}
    for line in lines:
        val = getattr(line, field_name, None)
        if val is None:
            continue
        key = str(val)
        if key not in buckets:
            buckets[key] = RankEntry(value=key, count=0)
        buckets[key].count += 1
        buckets[key].lines.append(line)
    return RankResult(entries=list(buckets.values()))


def format_rank(result: RankResult, n: int = 10, least: bool = False) -> str:
    entries = result.bottom(n) if least else result.top(n)
    lines = []
    for i, e in enumerate(entries, 1):
        lines.append(f"{i:>3}. [{e.count:>5}]  {e.value}")
    return "\n".join(lines) if lines else "(no results)"

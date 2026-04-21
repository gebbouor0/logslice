"""Trim leading and/or trailing lines from a log stream by count or predicate."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Optional

from logslice.parser import LogLine


@dataclass
class TrimResult:
    lines: List[LogLine]
    trimmed_head: int
    trimmed_tail: int

    def __len__(self) -> int:
        return len(self.lines)

    @property
    def total_trimmed(self) -> int:
        return self.trimmed_head + self.trimmed_tail


def trim_head(
    lines: List[LogLine],
    count: int = 0,
    predicate: Optional[Callable[[LogLine], bool]] = None,
) -> TrimResult:
    """Remove lines from the front by count or while predicate holds."""
    if count < 0:
        raise ValueError("count must be >= 0")
    if predicate is not None:
        idx = 0
        while idx < len(lines) and predicate(lines[idx]):
            idx += 1
        return TrimResult(lines=lines[idx:], trimmed_head=idx, trimmed_tail=0)
    trimmed = min(count, len(lines))
    return TrimResult(lines=lines[trimmed:], trimmed_head=trimmed, trimmed_tail=0)


def trim_tail(
    lines: List[LogLine],
    count: int = 0,
    predicate: Optional[Callable[[LogLine], bool]] = None,
) -> TrimResult:
    """Remove lines from the end by count or while predicate holds (scanning from tail)."""
    if count < 0:
        raise ValueError("count must be >= 0")
    if predicate is not None:
        idx = len(lines)
        while idx > 0 and predicate(lines[idx - 1]):
            idx -= 1
        trimmed = len(lines) - idx
        return TrimResult(lines=lines[:idx], trimmed_head=0, trimmed_tail=trimmed)
    trimmed = min(count, len(lines))
    end = len(lines) - trimmed
    return TrimResult(lines=lines[:end], trimmed_head=0, trimmed_tail=trimmed)


def trim_lines(
    lines: List[LogLine],
    head: int = 0,
    tail: int = 0,
    predicate: Optional[Callable[[LogLine], bool]] = None,
) -> TrimResult:
    """Trim both ends. Predicate is applied to both head and tail if provided."""
    head_result = trim_head(lines, count=head, predicate=predicate)
    tail_result = trim_tail(head_result.lines, count=tail, predicate=predicate)
    return TrimResult(
        lines=tail_result.lines,
        trimmed_head=head_result.trimmed_head,
        trimmed_tail=tail_result.trimmed_tail,
    )

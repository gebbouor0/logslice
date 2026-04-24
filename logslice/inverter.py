"""inverter.py — invert a filter: keep lines that do NOT match given patterns."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable, List, Optional

from logslice.parser import LogLine


@dataclass
class InvertedLine:
    _raw: str
    _line_number: int
    message: str
    timestamp: object  # datetime | None
    level: Optional[str]

    @property
    def raw(self) -> str:
        return self._raw

    @property
    def line_number(self) -> int:
        return self._line_number


@dataclass
class InvertResult:
    kept: List[InvertedLine] = field(default_factory=list)
    dropped: List[InvertedLine] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.kept)

    @property
    def total_input(self) -> int:
        return len(self.kept) + len(self.dropped)

    @property
    def drop_rate(self) -> float:
        if self.total_input == 0:
            return 0.0
        return len(self.dropped) / self.total_input


def _to_inverted(line: LogLine) -> InvertedLine:
    return InvertedLine(
        _raw=line.raw,
        _line_number=line.line_number,
        message=line.message,
        timestamp=line.timestamp,
        level=getattr(line, "level", None),
    )


def invert_lines(
    lines: Iterable[LogLine],
    patterns: List[str],
    case_sensitive: bool = False,
) -> InvertResult:
    """Keep lines that match NONE of the given patterns."""
    flags = 0 if case_sensitive else re.IGNORECASE
    compiled = [re.compile(p, flags) for p in patterns]
    result = InvertResult()
    for line in lines:
        matched = any(rx.search(line.message) for rx in compiled)
        inv = _to_inverted(line)
        if matched:
            result.dropped.append(inv)
        else:
            result.kept.append(inv)
    return result


def format_inverted(result: InvertResult) -> List[str]:
    """Return formatted strings for kept lines."""
    out = []
    for inv in result.kept:
        ts = str(inv.timestamp) if inv.timestamp else "-"
        out.append(f"[{inv.line_number}] {ts} {inv.message}")
    return out

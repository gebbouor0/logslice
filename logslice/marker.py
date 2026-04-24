"""marker.py — annotate log lines with positional markers (first, last, nth, pattern-based)."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, List, Optional
from logslice.parser import LogLine


@dataclass
class MarkedLine:
    _line: LogLine
    marker: Optional[str] = None

    @property
    def raw(self) -> str:
        return self._line.raw

    @property
    def line_number(self) -> int:
        return self._line.line_number

    @property
    def message(self) -> str:
        return self._line.message


@dataclass
class MarkResult:
    lines: List[MarkedLine] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.lines)

    def marked(self) -> List[MarkedLine]:
        return [l for l in self.lines if l.marker is not None]

    def unmarked(self) -> List[MarkedLine]:
        return [l for l in self.lines if l.marker is None]


def mark_lines(
    lines: List[LogLine],
    predicate: Callable[[LogLine], bool],
    marker: str = "*",
    mark_first: bool = False,
    mark_last: bool = False,
    every_nth: int = 0,
) -> MarkResult:
    """Apply markers to lines matching predicate or positional rules."""
    result: List[MarkedLine] = []
    total = len(lines)
    for i, line in enumerate(lines):
        m: Optional[str] = None
        if predicate(line):
            m = marker
        elif mark_first and i == 0:
            m = "first"
        elif mark_last and i == total - 1:
            m = "last"
        elif every_nth > 0 and i % every_nth == 0:
            m = f"nth({every_nth})"
        result.append(MarkedLine(_line=line, marker=m))
    return MarkResult(lines=result)


def format_marked(result: MarkResult) -> List[str]:
    out = []
    for ml in result.lines:
        prefix = f"[{ml.marker}] " if ml.marker else "      "
        out.append(f"{prefix}{ml.line_number:>4}: {ml.message}")
    return out

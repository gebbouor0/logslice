"""cutter.py — extract a slice of lines by index range (head/tail offsets)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from logslice.parser import LogLine


@dataclass
class CutResult:
    lines: List[LogLine] = field(default_factory=list)
    total_input: int = 0
    start_index: int = 0
    end_index: int = 0

    def __len__(self) -> int:
        return len(self.lines)

    @property
    def dropped_head(self) -> int:
        return self.start_index

    @property
    def dropped_tail(self) -> int:
        return max(0, self.total_input - self.end_index)


def cut_lines(
    lines: List[LogLine],
    start: Optional[int] = None,
    end: Optional[int] = None,
) -> CutResult:
    """Return lines[start:end] using Python slice semantics.

    Both *start* and *end* are 0-based indices and may be negative.
    Omitting either defaults to the natural list boundary.
    """
    total = len(lines)
    # resolve to concrete non-negative indices for reporting
    resolved_start = 0 if start is None else (start if start >= 0 else max(0, total + start))
    resolved_end = total if end is None else (end if end >= 0 else max(0, total + end))
    resolved_end = min(resolved_end, total)
    resolved_start = min(resolved_start, total)

    sliced = lines[start:end]
    return CutResult(
        lines=sliced,
        total_input=total,
        start_index=resolved_start,
        end_index=resolved_end,
    )


def format_cut(result: CutResult) -> List[str]:
    """Return formatted strings for each line in the cut result."""
    out: List[str] = []
    for line in result.lines:
        ts = line.timestamp.isoformat() if line.timestamp else "-"
        out.append(f"[{line.line_number}] {ts} {line.message}")
    return out

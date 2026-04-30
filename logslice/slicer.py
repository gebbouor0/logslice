"""slicer — extract a named sub-range from a list of LogLines by index or timestamp range."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from logslice.parser import LogLine


@dataclass
class Slice:
    lines: List[LogLine] = field(default_factory=list)
    start_index: int = 0
    end_index: int = 0
    label: str = ""

    def __len__(self) -> int:
        return len(self.lines)

    @property
    def is_empty(self) -> bool:
        return len(self.lines) == 0


@dataclass
class SliceResult:
    slices: List[Slice] = field(default_factory=list)
    total_input: int = 0

    def __len__(self) -> int:
        return len(self.slices)


def slice_by_index(
    lines: List[LogLine],
    start: int = 0,
    end: Optional[int] = None,
    label: str = "slice",
) -> SliceResult:
    end = end if end is not None else len(lines)
    start = max(0, start)
    end = min(end, len(lines))
    chunk = lines[start:end]
    s = Slice(lines=chunk, start_index=start, end_index=end - 1 if chunk else start, label=label)
    return SliceResult(slices=[s], total_input=len(lines))


def slice_by_timestamp(
    lines: List[LogLine],
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    label: str = "ts-slice",
) -> SliceResult:
    filtered = [
        l for l in lines
        if l.timestamp is not None
        and (start is None or l.timestamp >= start)
        and (end is None or l.timestamp <= end)
    ]
    indices = [lines.index(l) for l in filtered]
    s = Slice(
        lines=filtered,
        start_index=indices[0] if indices else 0,
        end_index=indices[-1] if indices else 0,
        label=label,
    )
    return SliceResult(slices=[s], total_input=len(lines))


def format_slice(result: SliceResult) -> List[str]:
    out: List[str] = []
    for s in result.slices:
        out.append(
            f"[{s.label}] lines={len(s)} idx={s.start_index}..{s.end_index}"
        )
        for line in s.lines:
            ts = line.timestamp.isoformat() if line.timestamp else "—"
            out.append(f"  {line.line_number:>4} {ts}  {line.message}")
    return out

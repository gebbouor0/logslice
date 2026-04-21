"""Smooth log streams by filling timestamp gaps with interpolated entries."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional

from logslice.parser import LogLine


@dataclass
class SmoothedLine:
    log_line: LogLine
    interpolated: bool = False

    @property
    def raw(self) -> str:
        return self.log_line.raw

    @property
    def line_number(self) -> Optional[int]:
        return self.log_line.line_number

    @property
    def timestamp(self) -> Optional[datetime]:
        return self.log_line.timestamp


@dataclass
class SmoothResult:
    lines: List[SmoothedLine] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.lines)

    @property
    def interpolated_count(self) -> int:
        return sum(1 for ln in self.lines if ln.interpolated)

    @property
    def original_count(self) -> int:
        return sum(1 for ln in self.lines if not ln.interpolated)


def smooth_lines(
    lines: List[LogLine],
    max_gap: timedelta,
    fill_message: str = "[gap]",
) -> SmoothResult:
    """Insert synthetic gap markers wherever consecutive timestamps exceed *max_gap*."""
    result = SmoothResult()
    if not lines:
        return result

    prev_ts: Optional[datetime] = None

    for log_line in lines:
        ts = log_line.timestamp
        if prev_ts is not None and ts is not None and (ts - prev_ts) > max_gap:
            gap_line = LogLine(
                raw=fill_message,
                timestamp=prev_ts + (ts - prev_ts) / 2,
                message=fill_message,
                level=None,
                line_number=None,
            )
            result.lines.append(SmoothedLine(log_line=gap_line, interpolated=True))
        result.lines.append(SmoothedLine(log_line=log_line, interpolated=False))
        if ts is not None:
            prev_ts = ts

    return result


def format_smoothed(result: SmoothResult) -> List[str]:
    """Return a list of formatted strings, marking interpolated lines."""
    out: List[str] = []
    for sl in result.lines:
        prefix = "~" if sl.interpolated else " "
        ts_str = sl.timestamp.isoformat() if sl.timestamp else "no-timestamp"
        out.append(f"{prefix} [{ts_str}] {sl.log_line.message or sl.raw}")
    return out

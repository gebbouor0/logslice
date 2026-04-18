"""Sliding/tumbling window over log lines by time interval."""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional
from logslice.parser import LogLine


@dataclass
class Window:
    start: datetime
    end: datetime
    lines: List[LogLine] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.lines)


def window_lines(
    lines: List[LogLine],
    interval: timedelta,
    slide: Optional[timedelta] = None,
) -> List[Window]:
    """Split lines into tumbling (or sliding) windows by timestamp.

    Lines without timestamps are skipped.
    If slide is None, windows are tumbling (non-overlapping).
    """
    if interval.total_seconds() <= 0:
        raise ValueError("interval must be positive")

    step = slide if slide is not None else interval
    if step.total_seconds() <= 0:
        raise ValueError("slide must be positive")

    stamped = [l for l in lines if l.timestamp is not None]
    if not stamped:
        return []

    first_ts: datetime = stamped[0].timestamp  # type: ignore[assignment]
    last_ts: datetime = stamped[-1].timestamp  # type: ignore[assignment]

    windows: List[Window] = []
    current = first_ts
    while current <= last_ts:
        end = current + interval
        w = Window(start=current, end=end)
        for line in stamped:
            ts: datetime = line.timestamp  # type: ignore[assignment]
            if current <= ts < end:
                w.lines.append(line)
        windows.append(w)
        current += step

    return windows


def format_windows(windows: List[Window]) -> str:
    parts: List[str] = []
    for i, w in enumerate(windows):
        header = f"[Window {i + 1}] {w.start.isoformat()} -> {w.end.isoformat()} ({len(w)} lines)"
        body = "\n".join(f"  {l.message}" for l in w.lines)
        parts.append(header + ("\n" + body if body else ""))
    return "\n".join(parts)

"""Throttle log lines to at most N lines per time window."""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional
from logslice.parser import LogLine


@dataclass
class ThrottleResult:
    lines: List[LogLine]
    dropped: int
    window_seconds: int
    max_per_window: int

    @property
    def kept(self) -> int:
        return len(self.lines)


def throttle_lines(
    lines: List[LogLine],
    max_per_window: int,
    window_seconds: int = 60,
) -> ThrottleResult:
    """Keep at most max_per_window lines per time window.

    Lines without timestamps are always kept.
    """
    if max_per_window < 1:
        raise ValueError("max_per_window must be >= 1")
    if window_seconds < 1:
        raise ValueError("window_seconds must be >= 1")

    kept: List[LogLine] = []
    dropped = 0
    window_start: Optional[datetime] = None
    count_in_window = 0

    for line in lines:
        if line.timestamp is None:
            kept.append(line)
            continue

        if window_start is None:
            window_start = line.timestamp
            count_in_window = 0

        delta = (line.timestamp - window_start).total_seconds()
        if delta >= window_seconds:
            window_start = line.timestamp
            count_in_window = 0

        if count_in_window < max_per_window:
            kept.append(line)
            count_in_window += 1
        else:
            dropped += 1

    return ThrottleResult(
        lines=kept,
        dropped=dropped,
        window_seconds=window_seconds,
        max_per_window=max_per_window,
    )

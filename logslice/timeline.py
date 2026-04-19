"""Build a chronological timeline view of log lines bucketed by time interval."""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from logslice.parser import LogLine


@dataclass
class TimelineBucket:
    start: datetime
    end: datetime
    lines: List[LogLine] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.lines)


@dataclass
class Timeline:
    interval_seconds: int
    buckets: List[TimelineBucket] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.buckets)

    def total_lines(self) -> int:
        return sum(len(b) for b in self.buckets)


def build_timeline(lines: List[LogLine], interval_seconds: int = 60) -> Timeline:
    """Group lines into fixed-width time buckets."""
    if interval_seconds <= 0:
        raise ValueError("interval_seconds must be positive")

    tl = Timeline(interval_seconds=interval_seconds)
    timestamped = [l for l in lines if l.timestamp is not None]
    if not timestamped:
        return tl

    delta = timedelta(seconds=interval_seconds)
    start = timestamped[0].timestamp
    bucket_start = start.replace(second=0, microsecond=0)
    current = TimelineBucket(start=bucket_start, end=bucket_start + delta)

    for line in timestamped:
        while line.timestamp >= current.end:
            tl.buckets.append(current)
            current = TimelineBucket(start=current.end, end=current.end + delta)
        current.lines.append(line)

    if current.lines:
        tl.buckets.append(current)

    return tl


def format_timeline(tl: Timeline, bar_width: int = 20) -> str:
    """Render a simple ASCII timeline."""
    if not tl.buckets:
        return "(no timestamped lines)"
    max_count = max(len(b) for b in tl.buckets) or 1
    rows = []
    for b in tl.buckets:
        filled = int(len(b) / max_count * bar_width)
        bar = "#" * filled + "." * (bar_width - filled)
        rows.append(f"{b.start.strftime('%H:%M:%S')} [{bar}] {len(b):>4}")
    return "\n".join(rows)

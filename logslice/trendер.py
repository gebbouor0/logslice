# logslice/trender.py
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from logslice.parser import LogLine


@dataclass
class TrendPoint:
    bucket_start: datetime
    count: int
    label: str = ""

    def __len__(self) -> int:
        return self.count


@dataclass
class TrendResult:
    points: List[TrendPoint] = field(default_factory=list)
    interval_seconds: int = 60
    skipped: int = 0

    def __len__(self) -> int:
        return len(self.points)

    @property
    def total_lines(self) -> int:
        return sum(p.count for p in self.points)

    @property
    def peak(self) -> Optional[TrendPoint]:
        return max(self.points, key=lambda p: p.count) if self.points else None

    @property
    def trough(self) -> Optional[TrendPoint]:
        return min(self.points, key=lambda p: p.count) if self.points else None


def build_trend(
    lines: List[LogLine],
    interval_seconds: int = 60,
) -> TrendResult:
    if interval_seconds <= 0:
        raise ValueError("interval_seconds must be positive")

    buckets: Dict[datetime, int] = {}
    skipped = 0

    for line in lines:
        if line.timestamp is None:
            skipped += 1
            continue
        bucket_ts = _floor_to_interval(line.timestamp, interval_seconds)
        buckets[bucket_ts] = buckets.get(bucket_ts, 0) + 1

    points = [
        TrendPoint(
            bucket_start=ts,
            count=count,
            label=ts.strftime("%Y-%m-%d %H:%M:%S"),
        )
        for ts, count in sorted(buckets.items())
    ]

    return TrendResult(points=points, interval_seconds=interval_seconds, skipped=skipped)


def _floor_to_interval(ts: datetime, interval_seconds: int) -> datetime:
    epoch = datetime(ts.year, ts.month, ts.day, tzinfo=ts.tzinfo)
    delta = (ts - epoch).total_seconds()
    floored = (delta // interval_seconds) * interval_seconds
    return epoch + timedelta(seconds=floored)


def format_trend(result: TrendResult) -> str:
    if not result.points:
        return "(no trend data)"
    lines = []
    max_count = max(p.count for p in result.points) or 1
    bar_width = 30
    for point in result.points:
        bar_len = int((point.count / max_count) * bar_width)
        bar = "#" * bar_len
        lines.append(f"{point.label}  {bar:<{bar_width}}  {point.count}")
    return "\n".join(lines)

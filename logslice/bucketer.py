"""Bucket log lines into fixed-size time windows and count occurrences."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional, Dict

from logslice.parser import LogLine


@dataclass
class Bucket:
    start: datetime
    end: datetime
    lines: List[LogLine] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.lines)

    @property
    def label(self) -> str:
        return self.start.strftime("%Y-%m-%d %H:%M:%S")


@dataclass
class BucketResult:
    buckets: List[Bucket]
    interval_seconds: int
    skipped: int  # lines without timestamps

    def __len__(self) -> int:
        return len(self.buckets)

    @property
    def total_bucketed(self) -> int:
        return sum(len(b) for b in self.buckets)


def bucket_lines(
    lines: List[LogLine],
    interval_seconds: int = 60,
) -> BucketResult:
    """Partition lines into time buckets of fixed duration."""
    if interval_seconds <= 0:
        raise ValueError("interval_seconds must be positive")

    timestamped = [l for l in lines if l.timestamp is not None]
    skipped = len(lines) - len(timestamped)

    if not timestamped:
        return BucketResult(buckets=[], interval_seconds=interval_seconds, skipped=skipped)

    delta = timedelta(seconds=interval_seconds)
    bucket_map: Dict[datetime, Bucket] = {}

    origin = min(l.timestamp for l in timestamped)  # type: ignore[type-var]

    for line in timestamped:
        offset = int((line.timestamp - origin).total_seconds() // interval_seconds)  # type: ignore[operator]
        bucket_start = origin + delta * offset
        bucket_end = bucket_start + delta
        if bucket_start not in bucket_map:
            bucket_map[bucket_start] = Bucket(start=bucket_start, end=bucket_end)
        bucket_map[bucket_start].lines.append(line)

    buckets = [bucket_map[k] for k in sorted(bucket_map)]
    return BucketResult(buckets=buckets, interval_seconds=interval_seconds, skipped=skipped)


def format_buckets(result: BucketResult) -> str:
    """Render a simple text summary of bucketed line counts."""
    if not result.buckets:
        return "(no bucketed lines)"
    lines = []
    for b in result.buckets:
        bar = "#" * len(b)
        lines.append(f"{b.label}  {len(b):>5}  {bar}")
    lines.append(f"total: {result.total_bucketed}, skipped: {result.skipped}")
    return "\n".join(lines)

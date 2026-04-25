"""Resampler: re-bucket log lines into a new time interval."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional

from logslice.parser import LogLine


@dataclass
class ResampledBucket:
    label: str
    interval_seconds: int
    lines: List[LogLine] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.lines)

    @property
    def start(self) -> Optional[datetime]:
        for ln in self.lines:
            if ln.timestamp:
                return ln.timestamp
        return None

    @property
    def end(self) -> Optional[datetime]:
        for ln in reversed(self.lines):
            if ln.timestamp:
                return ln.timestamp
        return None


@dataclass
class ResampleResult:
    buckets: List[ResampledBucket]
    skipped: int
    interval_seconds: int

    def __len__(self) -> int:
        return len(self.buckets)

    @property
    def total_bucketed(self) -> int:
        return sum(len(b) for b in self.buckets)


def _bucket_label(dt: datetime, interval_seconds: int) -> str:
    epoch = datetime(1970, 1, 1)
    slot = int((dt - epoch).total_seconds() // interval_seconds)
    bucket_start = epoch + timedelta(seconds=slot * interval_seconds)
    return bucket_start.strftime("%Y-%m-%dT%H:%M:%S")


def resample_lines(lines: List[LogLine], interval_seconds: int = 60) -> ResampleResult:
    if interval_seconds <= 0:
        raise ValueError("interval_seconds must be positive")

    buckets: dict[str, ResampledBucket] = {}
    skipped = 0

    for ln in lines:
        if not ln.timestamp:
            skipped += 1
            continue
        label = _bucket_label(ln.timestamp, interval_seconds)
        if label not in buckets:
            buckets[label] = ResampledBucket(label=label, interval_seconds=interval_seconds)
        buckets[label].lines.append(ln)

    ordered = [buckets[k] for k in sorted(buckets)]
    return ResampleResult(buckets=ordered, skipped=skipped, interval_seconds=interval_seconds)


def format_resampled(result: ResampleResult) -> List[str]:
    rows: List[str] = []
    for b in result.buckets:
        rows.append(f"[{b.label}] ({b.interval_seconds}s) — {len(b)} line(s)")
    if not rows:
        rows.append("(no buckets — all lines lacked timestamps)")
    return rows

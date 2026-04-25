"""flusher.py — periodically flush buffered log lines into fixed-size or time-bounded batches."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional

from logslice.parser import LogLine


@dataclass
class FlushBatch:
    index: int
    lines: List[LogLine] = field(default_factory=list)
    flushed_at: Optional[datetime] = None

    def __len__(self) -> int:
        return len(self.lines)

    @property
    def start_time(self) -> Optional[datetime]:
        for ln in self.lines:
            if ln.timestamp:
                return ln.timestamp
        return None

    @property
    def end_time(self) -> Optional[datetime]:
        for ln in reversed(self.lines):
            if ln.timestamp:
                return ln.timestamp
        return None


@dataclass
class FlushResult:
    batches: List[FlushBatch] = field(default_factory=list)
    total_input: int = 0

    def __len__(self) -> int:
        return len(self.batches)

    @property
    def total_flushed(self) -> int:
        return sum(len(b) for b in self.batches)


def flush_by_size(lines: List[LogLine], batch_size: int) -> FlushResult:
    """Split lines into batches of at most *batch_size* lines."""
    if batch_size < 1:
        raise ValueError("batch_size must be >= 1")
    result = FlushResult(total_input=len(lines))
    for i, start in enumerate(range(0, len(lines), batch_size)):
        chunk = lines[start : start + batch_size]
        result.batches.append(FlushBatch(index=i, lines=chunk))
    return result


def flush_by_interval(lines: List[LogLine], interval_seconds: float) -> FlushResult:
    """Split lines into batches where each batch spans at most *interval_seconds*."""
    if interval_seconds <= 0:
        raise ValueError("interval_seconds must be > 0")
    result = FlushResult(total_input=len(lines))
    if not lines:
        return result

    delta = timedelta(seconds=interval_seconds)
    batch_index = 0
    current = FlushBatch(index=batch_index)
    window_start: Optional[datetime] = None

    for ln in lines:
        if ln.timestamp is None:
            current.lines.append(ln)
            continue
        if window_start is None:
            window_start = ln.timestamp
        if ln.timestamp - window_start > delta:
            result.batches.append(current)
            batch_index += 1
            current = FlushBatch(index=batch_index)
            window_start = ln.timestamp
        current.lines.append(ln)

    if current.lines:
        result.batches.append(current)

    return result


def format_flush_summary(result: FlushResult) -> str:
    lines = [f"FlushResult: {len(result)} batches, {result.total_flushed}/{result.total_input} lines flushed"]
    for b in result.batches:
        start = b.start_time.isoformat() if b.start_time else "-"
        end = b.end_time.isoformat() if b.end_time else "-"
        lines.append(f"  batch[{b.index}]: {len(b)} lines  [{start} -> {end}]")
    return "\n".join(lines)

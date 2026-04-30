"""splitter4 — split a log stream into segments by a fixed line count or time duration boundary."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional

from logslice.parser import LogLine


@dataclass
class TimedSegment:
    index: int
    lines: List[LogLine] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    def __len__(self) -> int:
        return len(self.lines)


@dataclass
class TimedSplitResult:
    segments: List[TimedSegment] = field(default_factory=list)
    total_input: int = 0
    skipped: int = 0

    def __len__(self) -> int:
        return len(self.segments)

    @property
    def total_lines(self) -> int:
        return sum(len(s) for s in self.segments)


def split_by_line_count(lines: List[LogLine], count: int) -> TimedSplitResult:
    if count < 1:
        raise ValueError("count must be >= 1")
    result = TimedSplitResult(total_input=len(lines))
    for i in range(0, len(lines), count):
        chunk = lines[i : i + count]
        ts_list = [l.timestamp for l in chunk if l.timestamp]
        seg = TimedSegment(
            index=len(result.segments),
            lines=chunk,
            start_time=ts_list[0] if ts_list else None,
            end_time=ts_list[-1] if ts_list else None,
        )
        result.segments.append(seg)
    return result


def split_by_duration(lines: List[LogLine], seconds: float) -> TimedSplitResult:
    if seconds <= 0:
        raise ValueError("seconds must be > 0")
    result = TimedSplitResult(total_input=len(lines))
    current: Optional[TimedSegment] = None
    boundary: Optional[datetime] = None
    delta = timedelta(seconds=seconds)

    for line in lines:
        if line.timestamp is None:
            result.skipped += 1
            continue
        if current is None or line.timestamp >= boundary:  # type: ignore[operator]
            current = TimedSegment(index=len(result.segments), start_time=line.timestamp)
            boundary = line.timestamp + delta
            result.segments.append(current)
        current.lines.append(line)
        current.end_time = line.timestamp

    return result


def format_segments(result: TimedSplitResult) -> List[str]:
    out: List[str] = []
    for seg in result.segments:
        start = seg.start_time.isoformat() if seg.start_time else "—"
        end = seg.end_time.isoformat() if seg.end_time else "—"
        out.append(f"[segment {seg.index}] lines={len(seg)} start={start} end={end}")
    return out

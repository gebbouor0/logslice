"""Profile log lines by measuring message length and timestamp density."""
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime, timedelta
from logslice.parser import LogLine


@dataclass
class ProfileResult:
    total_lines: int
    lines_with_timestamp: int
    avg_message_length: float
    min_message_length: int
    max_message_length: int
    duration: Optional[timedelta]
    lines_per_second: Optional[float]
    empty_messages: int

    @property
    def timestamp_coverage(self) -> float:
        if self.total_lines == 0:
            return 0.0
        return self.lines_with_timestamp / self.total_lines


def profile_lines(lines: List[LogLine]) -> ProfileResult:
    """Compute profile statistics for a list of log lines.

    Args:
        lines: Parsed log lines to analyse.

    Returns:
        A ProfileResult with aggregate metrics such as message length
        statistics, timestamp coverage, and throughput.
    """
    if not lines:
        return ProfileResult(
            total_lines=0,
            lines_with_timestamp=0,
            avg_message_length=0.0,
            min_message_length=0,
            max_message_length=0,
            duration=None,
            lines_per_second=None,
            empty_messages=0,
        )

    messages = [l.message or "" for l in lines]
    lengths = [len(m) for m in messages]
    empty = sum(1 for m in messages if m.strip() == "")
    timestamped = [l for l in lines if l.timestamp is not None]

    duration: Optional[timedelta] = None
    lps: Optional[float] = None
    if len(timestamped) >= 2:
        ts_sorted = sorted(t.timestamp for t in timestamped)
        duration = ts_sorted[-1] - ts_sorted[0]
        secs = duration.total_seconds()
        if secs > 0:
            lps = len(lines) / secs

    return ProfileResult(
        total_lines=len(lines),
        lines_with_timestamp=len(timestamped),
        avg_message_length=sum(lengths) / len(lengths),
        min_message_length=min(lengths),
        max_message_length=max(lengths),
        duration=duration,
        lines_per_second=lps,
        empty_messages=empty,
    )


def format_profile(result: ProfileResult) -> str:
    """Format a ProfileResult as a human-readable string."""
    lines = [
        f"Total lines       : {result.total_lines}",
        f"With timestamp    : {result.lines_with_timestamp} ({result.timestamp_coverage:.1%})",
        f"Avg msg length    : {result.avg_message_length:.1f}",
        f"Min/Max msg length: {result.min_message_length} / {result.max_message_length}",
        f"Empty messages    : {result.empty_messages}",
        f"Duration          : {result.duration if result.duration is not None else 'N/A'}",
        f"Lines/second      : {f'{result.lines_per_second:.2f}' if result.lines_per_second is not None else 'N/A'}",
    ]
    return "\n".join(lines)

"""Detect consecutive streaks of matching log lines."""
from dataclasses import dataclass, field
from typing import List, Optional, Callable
from datetime import datetime
from logslice.parser import LogLine


@dataclass
class Streak:
    lines: List[LogLine] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    def __len__(self) -> int:
        return len(self.lines)

    @property
    def duration_seconds(self) -> Optional[float]:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None


@dataclass
class StreakResult:
    streaks: List[Streak] = field(default_factory=list)
    total_input: int = 0
    total_matched: int = 0

    def __len__(self) -> int:
        return len(self.streaks)

    @property
    def longest(self) -> Optional[Streak]:
        if not self.streaks:
            return None
        return max(self.streaks, key=len)


def detect_streaks(
    lines: List[LogLine],
    predicate: Callable[[LogLine], bool],
    min_length: int = 1,
) -> StreakResult:
    """Find consecutive runs of lines matching predicate."""
    if min_length < 1:
        raise ValueError("min_length must be >= 1")

    result = StreakResult(total_input=len(lines))
    current: Optional[Streak] = None

    for line in lines:
        if predicate(line):
            result.total_matched += 1
            if current is None:
                current = Streak()
            current.lines.append(line)
            if line.timestamp:
                if current.start_time is None:
                    current.start_time = line.timestamp
                current.end_time = line.timestamp
        else:
            if current is not None:
                if len(current) >= min_length:
                    result.streaks.append(current)
                current = None

    if current is not None and len(current) >= min_length:
        result.streaks.append(current)

    return result


def format_streaks(result: StreakResult) -> List[str]:
    """Format streak result as human-readable lines."""
    out = []
    out.append(f"Streaks found: {len(result)} (from {result.total_input} lines, {result.total_matched} matched)")
    for i, streak in enumerate(result.streaks, 1):
        dur = f", duration={streak.duration_seconds:.1f}s" if streak.duration_seconds is not None else ""
        out.append(f"  Streak {i}: {len(streak)} lines{dur}")
        for line in streak.lines:
            out.append(f"    [{line.line_number}] {line.message}")
    return out

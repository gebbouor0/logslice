"""Detect and report time gaps between consecutive log lines."""
from dataclasses import dataclass, field
from datetime import timedelta
from typing import List, Optional

from logslice.parser import LogLine


@dataclass
class Gap:
    before_line: LogLine
    after_line: LogLine
    duration: timedelta

    @property
    def seconds(self) -> float:
        return self.duration.total_seconds()

    def __repr__(self) -> str:
        return (
            f"Gap({self.seconds:.1f}s between "
            f"line {self.before_line.line_number} and "
            f"line {self.after_line.line_number})"
        )


@dataclass
class GapResult:
    gaps: List[Gap] = field(default_factory=list)
    total_lines: int = 0
    skipped_no_timestamp: int = 0

    def __len__(self) -> int:
        return len(self.gaps)

    @property
    def largest(self) -> Optional[Gap]:
        return max(self.gaps, key=lambda g: g.seconds) if self.gaps else None

    @property
    def smallest(self) -> Optional[Gap]:
        return min(self.gaps, key=lambda g: g.seconds) if self.gaps else None


def detect_gaps(lines: List[LogLine], min_seconds: float = 0.0) -> GapResult:
    """Find time gaps between consecutive timestamped lines.

    Args:
        lines: Parsed log lines to scan.
        min_seconds: Only report gaps at least this many seconds wide.

    Returns:
        GapResult with all qualifying gaps.
    """
    result = GapResult(total_lines=len(lines))
    prev: Optional[LogLine] = None

    for line in lines:
        if line.timestamp is None:
            result.skipped_no_timestamp += 1
            continue
        if prev is not None:
            delta = line.timestamp - prev.timestamp
            if delta.total_seconds() >= min_seconds:
                result.gaps.append(Gap(before_line=prev, after_line=line, duration=delta))
        prev = line

    return result


def format_gaps(result: GapResult) -> List[str]:
    """Render gap report as human-readable lines."""
    if not result.gaps:
        return ["No gaps detected."]
    rows = []
    for gap in result.gaps:
        rows.append(
            f"[GAP {gap.seconds:.1f}s] "
            f"line {gap.before_line.line_number} -> "
            f"line {gap.after_line.line_number}"
        )
    rows.append(f"Total gaps: {len(result.gaps)}")
    return rows

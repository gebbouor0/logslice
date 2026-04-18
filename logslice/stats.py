"""Compute summary statistics over a collection of log lines."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import List, Optional

from logslice.parser import LogLine


@dataclass
class LogStats:
    total: int = 0
    matched: int = 0
    levels: Counter = field(default_factory=Counter)
    earliest: Optional[str] = None
    latest: Optional[str] = None

    def summary(self) -> str:
        lines = [
            f"Total lines : {self.total}",
            f"Matched     : {self.matched}",
        ]
        if self.levels:
            level_str = ", ".join(f"{k}={v}" for k, v in sorted(self.levels.items()))
            lines.append(f"Levels      : {level_str}")
        if self.earliest:
            lines.append(f"Earliest    : {self.earliest}")
        if self.latest:
            lines.append(f"Latest      : {self.latest}")
        return "\n".join(lines)


_LEVEL_TOKENS = {"ERROR", "WARN", "WARNING", "INFO", "DEBUG", "CRITICAL", "FATAL"}


def _extract_level(line: LogLine) -> Optional[str]:
    for token in _LEVEL_TOKENS:
        if token in line.raw.upper():
            return token
    return None


def compute_stats(all_lines: List[LogLine], matched_lines: List[LogLine]) -> LogStats:
    """Return statistics comparing all parsed lines against the filtered subset."""
    stats = LogStats(total=len(all_lines), matched=len(matched_lines))

    timestamps = [l.timestamp.isoformat() for l in all_lines if l.timestamp]
    if timestamps:
        stats.earliest = min(timestamps)
        stats.latest = max(timestamps)

    for line in matched_lines:
        level = _extract_level(line)
        if level:
            stats.levels[level] += 1

    return stats

"""Inspect a list of LogLines and produce a structured health overview."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from logslice.parser import LogLine

_LEVEL_KEYWORDS = {
    "error": ["error", "err", "critical", "fatal"],
    "warning": ["warn", "warning"],
    "info": ["info"],
    "debug": ["debug"],
}


def _detect_level(message: str) -> str:
    lower = message.lower()
    for level, keywords in _LEVEL_KEYWORDS.items():
        if any(kw in lower for kw in keywords):
            return level
    return "unknown"


@dataclass
class InspectionResult:
    total_lines: int
    lines_with_timestamp: int
    lines_without_timestamp: int
    level_counts: Dict[str, int]
    duplicate_count: int
    empty_message_count: int
    issues: List[str] = field(default_factory=list)

    @property
    def timestamp_coverage(self) -> float:
        if self.total_lines == 0:
            return 0.0
        return self.lines_with_timestamp / self.total_lines


def inspect_lines(lines: List[LogLine]) -> InspectionResult:
    """Analyse lines and return an InspectionResult with health metrics."""
    total = len(lines)
    with_ts = sum(1 for l in lines if l.timestamp is not None)
    without_ts = total - with_ts

    level_counts: Dict[str, int] = {}
    empty_count = 0
    seen_messages: Dict[str, int] = {}

    for line in lines:
        msg = line.message.strip()
        if not msg:
            empty_count += 1
        lvl = _detect_level(msg)
        level_counts[lvl] = level_counts.get(lvl, 0) + 1
        seen_messages[msg] = seen_messages.get(msg, 0) + 1

    duplicate_count = sum(v - 1 for v in seen_messages.values() if v > 1)

    issues: List[str] = []
    if without_ts > 0:
        issues.append(f"{without_ts} line(s) missing timestamps")
    if empty_count > 0:
        issues.append(f"{empty_count} empty message(s)")
    if duplicate_count > 0:
        issues.append(f"{duplicate_count} duplicate message(s)")
    error_count = level_counts.get("error", 0)
    if error_count > 0:
        issues.append(f"{error_count} error-level line(s) detected")

    return InspectionResult(
        total_lines=total,
        lines_with_timestamp=with_ts,
        lines_without_timestamp=without_ts,
        level_counts=level_counts,
        duplicate_count=duplicate_count,
        empty_message_count=empty_count,
        issues=issues,
    )


def format_inspection(result: InspectionResult) -> str:
    lines = [
        f"Inspection report ({result.total_lines} lines)",
        f"  Timestamp coverage : {result.timestamp_coverage:.1%}",
        f"  Empty messages     : {result.empty_message_count}",
        f"  Duplicates         : {result.duplicate_count}",
        "  Levels:",
    ]
    for lvl, cnt in sorted(result.level_counts.items()):
        lines.append(f"    {lvl:<10} {cnt}")
    if result.issues:
        lines.append("  Issues:")
        for issue in result.issues:
            lines.append(f"    ! {issue}")
    else:
        lines.append("  No issues found.")
    return "\n".join(lines)

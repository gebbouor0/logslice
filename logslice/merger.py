"""Merge multiple sorted log streams into a single time-ordered sequence."""

from __future__ import annotations

import heapq
from dataclasses import dataclass, field
from typing import Iterable, List, Optional

from logslice.parser import LogLine


@dataclass
class SourcedLine:
    """A log line annotated with its source label."""

    line: LogLine
    source: str

    def __lt__(self, other: "SourcedLine") -> bool:
        # Lines without timestamps go last
        if self.line.timestamp is None and other.line.timestamp is None:
            return self.line.line_number < other.line.line_number
        if self.line.timestamp is None:
            return False
        if other.line.timestamp is None:
            return True
        return self.line.timestamp < other.line.timestamp


def merge_streams(
    streams: Iterable[tuple[str, Iterable[LogLine]]],
) -> List[SourcedLine]:
    """Merge labelled log streams into a single time-ordered list.

    Args:
        streams: Iterable of (label, log_lines) pairs.

    Returns:
        List of SourcedLine sorted by timestamp then line_number.
    """
    heap: list[SourcedLine] = []
    for source, lines in streams:
        for log_line in lines:
            heapq.heappush(heap, SourcedLine(line=log_line, source=source))

    result: List[SourcedLine] = []
    while heap:
        result.append(heapq.heappop(heap))
    return result


def format_merged(sourced_lines: List[SourcedLine], show_source: bool = True) -> List[str]:
    """Format merged lines, optionally prefixing each with its source label."""
    out: List[str] = []
    for sl in sourced_lines:
        prefix = f"[{sl.source}] " if show_source else ""
        out.append(f"{prefix}{sl.line.raw}")
    return out

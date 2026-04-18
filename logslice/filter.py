"""Filtering logic for log lines by time range and regex pattern."""

import re
from datetime import datetime
from typing import Optional

from logslice.parser import LogLine


def filter_lines(
    lines: list[LogLine],
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    pattern: Optional[str] = None,
) -> list[LogLine]:
    """
    Filter log lines by optional time range and/or regex pattern.

    Lines without a timestamp are included only when no time filter is active.
    """
    compiled = re.compile(pattern) if pattern else None
    time_filter_active = start is not None or end is not None
    result = []

    for line in lines:
        if time_filter_active:
            if line.timestamp is None:
                continue
            if start and line.timestamp < start:
                continue
            if end and line.timestamp > end:
                continue

        if compiled and not compiled.search(line.raw):
            continue

        result.append(line)

    return result


def format_output(lines: list[LogLine], show_line_numbers: bool = False) -> str:
    """Format filtered log lines for output."""
    parts = []
    for line in lines:
        if show_line_numbers:
            parts.append(f"{line.line_number:>6}: {line.raw}")
        else:
            parts.append(line.raw)
    return "\n".join(parts)

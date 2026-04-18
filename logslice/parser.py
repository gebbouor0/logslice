"""Log line parsing utilities for extracting timestamps and patterns."""

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

# Common log timestamp formats to try
TIMESTAMP_FORMATS = [
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M:%S.%f",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d %H:%M:%S.%f",
    "%d/%b/%Y:%H:%M:%S",
]

TIMESTAMP_PATTERN = re.compile(
    r"(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?"
    r"|\d{2}/\w+/\d{4}:\d{2}:\d{2}:\d{2})"
)


@dataclass
class LogLine:
    raw: str
    timestamp: Optional[datetime]
    line_number: int


def parse_timestamp(text: str) -> Optional[datetime]:
    """Try to extract a datetime from a string using known formats."""
    match = TIMESTAMP_PATTERN.search(text)
    if not match:
        return None
    ts_str = match.group(1)
    for fmt in TIMESTAMP_FORMATS:
        try:
            return datetime.strptime(ts_str, fmt)
        except ValueError:
            continue
    return None


def parse_line(raw: str, line_number: int) -> LogLine:
    """Parse a single log line into a LogLine object."""
    return LogLine(
        raw=raw.rstrip("\n"),
        timestamp=parse_timestamp(raw),
        line_number=line_number,
    )


def parse_lines(lines) -> list[LogLine]:
    """Parse an iterable of raw log lines."""
    return [parse_line(line, i + 1) for i, line in enumerate(lines)]

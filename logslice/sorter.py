from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional
from logslice.parser import LogLine


@dataclass
class SortResult:
    lines: List[LogLine]
    strategy: str
    reversed: bool


def sort_by_timestamp(lines: List[LogLine], reverse: bool = False) -> SortResult:
    """Sort lines by timestamp; lines without timestamps go last."""
    def key(line: LogLine):
        return (line.timestamp is None, line.timestamp)

    sorted_lines = sorted(lines, key=key, reverse=False)
    if reverse:
        sorted_lines = list(reversed(sorted_lines))
    return SortResult(lines=sorted_lines, strategy="timestamp", reversed=reverse)


def sort_by_message(lines: List[LogLine], reverse: bool = False) -> SortResult:
    """Sort lines alphabetically by message."""
    sorted_lines = sorted(lines, key=lambda l: l.message.lower(), reverse=reverse)
    return SortResult(lines=sorted_lines, strategy="message", reversed=reverse)


def sort_by_line_number(lines: List[LogLine], reverse: bool = False) -> SortResult:
    """Sort lines by original line number."""
    sorted_lines = sorted(lines, key=lambda l: (l.line_number is None, l.line_number or 0), reverse=reverse)
    return SortResult(lines=sorted_lines, strategy="line_number", reversed=reverse)


def sort_lines(lines: List[LogLine], strategy: str = "timestamp", reverse: bool = False) -> SortResult:
    """Sort lines using named strategy."""
    strategies = {
        "timestamp": sort_by_timestamp,
        "message": sort_by_message,
        "line_number": sort_by_line_number,
    }
    if strategy not in strategies:
        raise ValueError(f"Unknown sort strategy: {strategy!r}. Choose from {list(strategies)}")
    return strategies[strategy](lines, reverse=reverse)

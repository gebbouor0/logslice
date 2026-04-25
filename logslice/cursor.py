"""cursor.py — track a named read position within a log stream."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from logslice.parser import LogLine


@dataclass
class Cursor:
    name: str
    position: int = 0  # index into the line list
    last_timestamp: Optional[datetime] = None
    last_line_number: Optional[int] = None

    def advance(self, line: LogLine) -> None:
        self.position += 1
        if line.timestamp is not None:
            self.last_timestamp = line.timestamp
        self.last_line_number = line.line_number

    def is_at_start(self) -> bool:
        return self.position == 0


@dataclass
class CursorResult:
    cursor: Cursor
    remaining: List[LogLine] = field(default_factory=list)
    consumed: List[LogLine] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.consumed)


def seek_cursor(lines: List[LogLine], cursor: Cursor, count: int) -> CursorResult:
    """Advance cursor by *count* lines, returning consumed and remaining."""
    if count < 0:
        raise ValueError("count must be non-negative")

    start = cursor.position
    end = min(start + count, len(lines))
    consumed = lines[start:end]

    for line in consumed:
        cursor.advance(line)

    remaining = lines[cursor.position:]
    return CursorResult(cursor=cursor, consumed=consumed, remaining=remaining)


def reset_cursor(cursor: Cursor) -> Cursor:
    """Reset cursor back to the beginning of the stream."""
    cursor.position = 0
    cursor.last_timestamp = None
    cursor.last_line_number = None
    return cursor


def format_cursor(cursor: Cursor) -> str:
    ts = cursor.last_timestamp.isoformat() if cursor.last_timestamp else "-"
    ln = str(cursor.last_line_number) if cursor.last_line_number is not None else "-"
    return f"[cursor:{cursor.name}] pos={cursor.position} last_ts={ts} last_ln={ln}"

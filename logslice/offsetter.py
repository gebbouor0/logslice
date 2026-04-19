"""Shift log line numbers by a fixed offset (useful when merging partial files)."""
from dataclasses import dataclass
from typing import List
from logslice.parser import LogLine


@dataclass
class OffsetLine:
    original: LogLine
    offset: int

    @property
    def raw(self) -> str:
        return self.original.raw

    @property
    def line_number(self) -> int:
        return (self.original.line_number or 0) + self.offset

    @property
    def message(self) -> str:
        return self.original.message


@dataclass
class OffsetResult:
    lines: List[OffsetLine]
    offset: int

    def __len__(self) -> int:
        return len(self.lines)


def offset_lines(lines: List[LogLine], offset: int) -> OffsetResult:
    """Return all lines with line numbers shifted by *offset*."""
    shifted = [OffsetLine(original=line, offset=offset) for line in lines]
    return OffsetResult(lines=shifted, offset=offset)


def format_offset(result: OffsetResult) -> str:
    """Render offset lines as numbered text."""
    rows = [f"{ol.line_number:>6}: {ol.raw}" for ol in result.lines]
    return "\n".join(rows)

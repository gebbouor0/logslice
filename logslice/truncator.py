"""Truncate long log lines with optional ellipsis and field preservation."""
from dataclasses import dataclass
from typing import List, Optional
from logslice.parser import LogLine


@dataclass
class TruncatedLine:
    original: LogLine
    display: str
    was_truncated: bool

    @property
    def raw(self) -> str:
        return self.original.raw

    @property
    def line_number(self) -> Optional[int]:
        return self.original.line_number


def truncate_message(text: str, max_len: int, ellipsis: str = "...") -> tuple[str, bool]:
    """Truncate text to max_len, appending ellipsis if needed."""
    if max_len <= 0:
        raise ValueError("max_len must be positive")
    if len(text) <= max_len:
        return text, False
    cut = max_len - len(ellipsis)
    if cut < 0:
        return ellipsis[:max_len], True
    return text[:cut] + ellipsis, True


def truncate_line(line: LogLine, max_len: int, ellipsis: str = "...") -> TruncatedLine:
    """Truncate a single LogLine's raw text."""
    display, was_truncated = truncate_message(line.raw, max_len, ellipsis)
    return TruncatedLine(original=line, display=display, was_truncated=was_truncated)


def truncate_lines(
    lines: List[LogLine],
    max_len: int,
    ellipsis: str = "...",
) -> List[TruncatedLine]:
    """Truncate a list of LogLines."""
    return [truncate_line(line, max_len, ellipsis) for line in lines]


def format_truncated(truncated: List[TruncatedLine], mark_truncated: bool = False) -> List[str]:
    """Format truncated lines, optionally marking which were cut."""
    out = []
    for t in truncated:
        line = t.display
        if mark_truncated and t.was_truncated:
            line = f"{line} [truncated]"
        out.append(line)
    return out

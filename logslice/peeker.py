"""Peek ahead/behind in a log stream without consuming lines."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Optional

from logslice.parser import LogLine


@dataclass
class PeekWindow:
    """A line along with its surrounding context lines."""
    line: LogLine
    before: List[LogLine] = field(default_factory=list)
    after: List[LogLine] = field(default_factory=list)

    @property
    def raw(self) -> str:
        return self.line.raw

    @property
    def line_number(self) -> int:
        return self.line.line_number


@dataclass
class PeekResult:
    windows: List[PeekWindow] = field(default_factory=list)
    total_input: int = 0

    def __len__(self) -> int:
        return len(self.windows)


def peek_lines(
    lines: List[LogLine],
    predicate: Callable[[LogLine], bool],
    before: int = 2,
    after: int = 2,
) -> PeekResult:
    """Return a PeekWindow for every line matching *predicate*.

    Each window carries up to *before* preceding lines and up to *after*
    following lines (clamped at the stream boundaries).

    Args:
        lines: Input log lines.
        predicate: Selector — return True for lines you want to peek at.
        before: Number of lines to include before the matched line.
        after: Number of lines to include after the matched line.

    Returns:
        PeekResult containing one PeekWindow per matched line.
    """
    if before < 0 or after < 0:
        raise ValueError("before and after must be non-negative")

    result = PeekResult(total_input=len(lines))
    for idx, line in enumerate(lines):
        if not predicate(line):
            continue
        start = max(0, idx - before)
        end = min(len(lines), idx + after + 1)
        window = PeekWindow(
            line=line,
            before=lines[start:idx],
            after=lines[idx + 1:end],
        )
        result.windows.append(window)
    return result


def format_peek(result: PeekResult, separator: str = "---") -> List[str]:
    """Render peek windows as plain text lines."""
    output: List[str] = []
    for i, window in enumerate(result.windows):
        if i > 0:
            output.append(separator)
        for bl in window.before:
            output.append(f"  {bl.line_number:>6}  {bl.message}")
        output.append(f">> {window.line.line_number:>6}  {window.line.message}")
        for al in window.after:
            output.append(f"  {al.line_number:>6}  {al.message}")
    return output

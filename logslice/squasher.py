"""squasher.py — collapse runs of similar log lines into a single representative line with a repeat count."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from logslice.parser import LogLine


@dataclass
class SquashedLine:
    line: LogLine
    repeat_count: int = 1

    @property
    def raw(self) -> str:
        return self.line.raw

    @property
    def line_number(self) -> int:
        return self.line.line_number

    @property
    def message(self) -> str:
        return self.line.message

    def formatted(self) -> str:
        if self.repeat_count > 1:
            return f"{self.raw.rstrip()} [x{self.repeat_count}]"
        return self.raw.rstrip()


@dataclass
class SquashResult:
    lines: List[SquashedLine] = field(default_factory=list)
    total_input: int = 0

    def __len__(self) -> int:
        return len(self.lines)

    @property
    def total_squashed(self) -> int:
        """Number of lines that were merged away."""
        return self.total_input - len(self.lines)


def _normalize(message: Optional[str]) -> str:
    return (message or "").strip().lower()


def squash_lines(lines: List[LogLine], case_sensitive: bool = False) -> SquashResult:
    """Collapse consecutive lines with identical messages into one SquashedLine."""
    result = SquashResult(total_input=len(lines))
    if not lines:
        return result

    def key(msg: Optional[str]) -> str:
        return (msg or "").strip() if case_sensitive else _normalize(msg)

    current = SquashedLine(line=lines[0], repeat_count=1)
    for line in lines[1:]:
        if key(line.message) == key(current.line.message):
            current.repeat_count += 1
        else:
            result.lines.append(current)
            current = SquashedLine(line=line, repeat_count=1)
    result.lines.append(current)
    return result


def format_squashed(result: SquashResult) -> List[str]:
    return [sl.formatted() for sl in result.lines]

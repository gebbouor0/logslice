"""collapser.py — collapse consecutive similar log lines into a single representative line with a repeat count."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Optional

from logslice.parser import LogLine


@dataclass
class CollapsedLine:
    line: LogLine
    repeat_count: int = 1

    @property
    def raw(self) -> str:
        return self.line.raw

    @property
    def line_number(self) -> Optional[int]:
        return self.line.line_number

    @property
    def message(self) -> str:
        return self.line.message


@dataclass
class CollapseResult:
    items: List[CollapsedLine] = field(default_factory=list)
    total_input: int = 0
    total_output: int = 0

    @property
    def collapsed_count(self) -> int:
        """Number of lines that were merged away."""
        return self.total_input - self.total_output

    def __len__(self) -> int:
        return len(self.items)


def _default_key(line: LogLine) -> str:
    return line.message.strip()


def collapse_lines(
    lines: List[LogLine],
    key: Callable[[LogLine], str] = _default_key,
) -> CollapseResult:
    """Collapse consecutive lines that share the same key into one CollapsedLine."""
    result = CollapseResult(total_input=len(lines))
    if not lines:
        return result

    current_line = lines[0]
    current_key = key(current_line)
    count = 1

    for line in lines[1:]:
        k = key(line)
        if k == current_key:
            count += 1
        else:
            result.items.append(CollapsedLine(line=current_line, repeat_count=count))
            current_line = line
            current_key = k
            count = 1

    result.items.append(CollapsedLine(line=current_line, repeat_count=count))
    result.total_output = len(result.items)
    return result


def format_collapsed(result: CollapseResult) -> List[str]:
    """Format collapsed lines; repeated lines show an 'x N' suffix."""
    out = []
    for item in result.items:
        if item.repeat_count > 1:
            out.append(f"{item.raw.rstrip()} (x{item.repeat_count})")
        else:
            out.append(item.raw.rstrip())
    return out

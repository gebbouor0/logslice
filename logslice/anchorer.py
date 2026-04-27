"""anchorer.py — extract a fixed window of lines around a matched anchor line."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Optional

from logslice.parser import LogLine


@dataclass
class AnchorWindow:
    anchor: LogLine
    before: List[LogLine] = field(default_factory=list)
    after: List[LogLine] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.before) + 1 + len(self.after)

    @property
    def all_lines(self) -> List[LogLine]:
        return self.before + [self.anchor] + self.after


@dataclass
class AnchorResult:
    windows: List[AnchorWindow] = field(default_factory=list)
    total_input: int = 0

    def __len__(self) -> int:
        return len(self.windows)


def anchor_lines(
    lines: List[LogLine],
    predicate: Callable[[LogLine], bool],
    before: int = 2,
    after: int = 2,
) -> AnchorResult:
    """Return one AnchorWindow per line that satisfies *predicate*."""
    if before < 0 or after < 0:
        raise ValueError("before and after must be non-negative")

    result = AnchorResult(total_input=len(lines))
    for idx, line in enumerate(lines):
        if predicate(line):
            win_before = lines[max(0, idx - before): idx]
            win_after = lines[idx + 1: idx + 1 + after]
            result.windows.append(
                AnchorWindow(anchor=line, before=win_before, after=win_after)
            )
    return result


def format_anchored(result: AnchorResult, separator: str = "---") -> List[str]:
    """Render each window as a block of raw log strings separated by *separator*."""
    output: List[str] = []
    for i, window in enumerate(result.windows):
        if i > 0:
            output.append(separator)
        for log_line in window.all_lines:
            marker = ">>> " if log_line is window.anchor else "    "
            output.append(f"{marker}{log_line.raw}")
    return output

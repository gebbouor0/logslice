"""tapper.py — non-destructively tap into a log stream, applying a side-effect
callback on each line while passing lines through unchanged."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Iterable, List

from logslice.parser import LogLine


@dataclass
class TapResult:
    lines: List[LogLine] = field(default_factory=list)
    tap_count: int = 0

    def __len__(self) -> int:
        return len(self.lines)

    def __iter__(self):
        return iter(self.lines)


def tap_lines(
    lines: Iterable[LogLine],
    callback: Callable[[LogLine], None],
    *,
    predicate: Callable[[LogLine], bool] | None = None,
) -> TapResult:
    """Pass every line through unchanged; call *callback* for lines matching
    *predicate* (or all lines when predicate is None).  Returns a TapResult
    containing the original lines and a count of how many times the callback
    was invoked."""
    result_lines: List[LogLine] = []
    tap_count = 0

    for line in lines:
        result_lines.append(line)
        if predicate is None or predicate(line):
            callback(line)
            tap_count += 1

    return TapResult(lines=result_lines, tap_count=tap_count)


def format_tap_summary(result: TapResult) -> str:
    """Return a one-line summary of the tap operation."""
    total = len(result)
    return (
        f"tapped {result.tap_count}/{total} line(s) "
        f"({result.tap_count / total * 100:.1f}%)"
        if total
        else "tapped 0/0 lines"
    )

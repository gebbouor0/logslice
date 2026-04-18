"""Combine filtering, highlighting and stats into a final report."""

from __future__ import annotations

from typing import List, Optional

from logslice.parser import LogLine
from logslice.filter import filter_lines, format_output
from logslice.highlighter import highlight_lines
from logslice.stats import compute_stats, LogStats


@dataclass_like = None  # noqa – plain class, no dataclass needed


class Report:
    def __init__(
        self,
        output_lines: List[str],
        stats: LogStats,
    ) -> None:
        self.output_lines = output_lines
        self.stats = stats

    def render(self, show_stats: bool = False) -> str:
        parts = self.output_lines[:]
        if show_stats:
            parts.append("")
            parts.append("--- Stats ---")
            parts.append(self.stats.summary())
        return "\n".join(parts)


def build_report(
    all_lines: List[LogLine],
    *,
    start=None,
    end=None,
    pattern: Optional[str] = None,
    color: str = "yellow",
    context: int = 0,
) -> Report:
    """Filter, highlight and compute stats; return a Report."""
    matched = filter_lines(all_lines, start=start, end=end, pattern=pattern)

    if pattern:
        highlighted = highlight_lines(matched, pattern=pattern, color=color)
    else:
        highlighted = matched

    formatted = format_output(highlighted, context_lines=context, source=all_lines)
    stats = compute_stats(all_lines, matched)
    return Report(output_lines=formatted, stats=stats)

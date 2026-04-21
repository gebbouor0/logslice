"""Formatter: apply display options to LogLine sequences."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Sequence

from logslice.parser import LogLine


@dataclass
class FormatOptions:
    show_line_numbers: bool = False
    show_timestamps: bool = True
    timestamp_format: str = "%Y-%m-%d %H:%M:%S"
    max_width: Optional[int] = None


def format_line(line: LogLine, options: Optional[FormatOptions] = None) -> str:
    opts = options or FormatOptions()
    parts: List[str] = []

    if opts.show_line_numbers and line.line_number is not None:
        parts.append(f"[{line.line_number:>6}]")

    if opts.show_timestamps:
        if line.timestamp is not None:
            parts.append(line.timestamp.strftime(opts.timestamp_format))
        else:
            parts.append("(no timestamp)")

    parts.append(line.message or line.raw)

    result = "  ".join(parts)
    if opts.max_width and len(result) > opts.max_width:
        result = result[: opts.max_width - 3] + "..."
    return result


def format_lines(
    lines: Sequence[LogLine], options: Optional[FormatOptions] = None
) -> List[str]:
    return [format_line(line, options) for line in lines]

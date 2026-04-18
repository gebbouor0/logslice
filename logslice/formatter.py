from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional
from logslice.parser import LogLine


_LEVEL_COLORS = {
    "ERROR": "\033[31m",
    "WARN": "\033[33m",
    "WARNING": "\033[33m",
    "INFO": "\033[32m",
    "DEBUG": "\033[36m",
}
_RESET = "\033[0m"


@dataclass
class FormatOptions:
    show_line_numbers: bool = False
    show_timestamps: bool = True
    colorize_levels: bool = False
    timestamp_fmt: str = "%Y-%m-%d %H:%M:%S"
    separator: str = " | "


def format_line(line: LogLine, opts: Optional[FormatOptions] = None) -> str:
    """Format a single LogLine into a human-readable string."""
    if opts is None:
        opts = FormatOptions()

    parts: List[str] = []

    if opts.show_line_numbers and line.line_number is not None:
        parts.append(f"[{line.line_number}]")

    if opts.show_timestamps and line.timestamp is not None:
        parts.append(line.timestamp.strftime(opts.timestamp_fmt))

    if line.level:
        level_str = line.level.upper()
        if opts.colorize_levels and level_str in _LEVEL_COLORS:
            level_str = f"{_LEVEL_COLORS[level_str]}{level_str}{_RESET}"
        parts.append(level_str)

    parts.append(line.message)
    return opts.separator.join(parts)


def format_lines(lines: List[LogLine], opts: Optional[FormatOptions] = None) -> List[str]:
    """Format multiple LogLines."""
    return [format_line(line, opts) for line in lines]

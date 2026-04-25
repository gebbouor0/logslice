"""Formatter: render LogLine objects as human-readable strings."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from logslice.parser import LogLine


@dataclass
class FormatOptions:
    show_line_number: bool = True
    show_timestamp: bool = True
    show_level: bool = True
    timestamp_format: str = "%Y-%m-%dT%H:%M:%S"
    separator: str = " | "


def format_line(line: LogLine, options: Optional[FormatOptions] = None) -> str:
    if options is None:
        options = FormatOptions()

    parts: List[str] = []

    if options.show_line_number:
        parts.append(f"#{line.line_number}")

    if options.show_timestamp:
        if line.timestamp:
            parts.append(line.timestamp.strftime(options.timestamp_format))
        else:
            parts.append("-")

    if options.show_level:
        parts.append(line.level if line.level else "-")

    parts.append(line.message or line.raw)

    return options.separator.join(parts)


def format_lines(lines: List[LogLine], options: Optional[FormatOptions] = None) -> List[str]:
    return [format_line(ln, options) for ln in lines]

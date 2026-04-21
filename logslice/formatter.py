"""Format LogLine objects into human-readable strings."""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional
from logslice.parser import LogLine


@dataclass
class FormatOptions:
    show_line_number: bool = True
    show_timestamp: bool = True
    show_level: bool = False
    timestamp_format: str = "%Y-%m-%d %H:%M:%S"
    separator: str = " | "


def format_line(line: LogLine, opts: Optional[FormatOptions] = None) -> str:
    if opts is None:
        opts = FormatOptions()

    parts: List[str] = []

    if opts.show_line_number:
        parts.append(f"{line.line_number:>6}")

    if opts.show_timestamp:
        if line.timestamp is not None:
            parts.append(line.timestamp.strftime(opts.timestamp_format))
        else:
            parts.append("-")

    if opts.show_level:
        import re
        m = re.search(r'\b(DEBUG|INFO|WARNING|ERROR|CRITICAL)\b', line.message, re.IGNORECASE)
        level = m.group(1).upper() if m else "UNKNOWN"
        parts.append(f"[{level}]")

    parts.append(line.message)
    return opts.separator.join(parts)


def format_lines(lines: List[LogLine], opts: Optional[FormatOptions] = None) -> List[str]:
    return [format_line(line, opts) for line in lines]

"""Format LogLine objects for display output."""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional
from logslice.parser import LogLine

DEFAULT_TS_FORMAT = "%Y-%m-%dT%H:%M:%S"


@dataclass
class FormatOptions:
    show_line_numbers: bool = True
    show_timestamps: bool = True
    ts_format: str = DEFAULT_TS_FORMAT
    separator: str = " | "


def format_line(line: LogLine, opts: Optional[FormatOptions] = None) -> str:
    opts = opts or FormatOptions()
    parts: List[str] = []
    if opts.show_line_numbers and line.line_number is not None:
        parts.append(f"[{line.line_number}]")
    if opts.show_timestamps:
        if line.timestamp is not None:
            parts.append(line.timestamp.strftime(opts.ts_format))
        else:
            parts.append("(no timestamp)")
    parts.append(line.message or line.raw)
    return opts.separator.join(parts)


def format_lines(lines: List[LogLine], opts: Optional[FormatOptions] = None) -> List[str]:
    return [format_line(l, opts) for l in lines]

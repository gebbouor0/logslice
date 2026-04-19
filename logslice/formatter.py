"""Format log lines for display."""
from dataclasses import dataclass, field
from typing import List, Optional
from logslice.parser import LogLine


@dataclass
class FormatOptions:
    show_line_numbers: bool = True
    show_timestamps: bool = True
    timestamp_format: str = "%Y-%m-%d %H:%M:%S"
    separator: str = " | "


def format_line(line: LogLine, options: Optional[FormatOptions] = None) -> str:
    opts = options or FormatOptions()
    parts = []
    if opts.show_line_numbers:
        parts.append(f"{line.line_number:>6}")
    if opts.show_timestamps:
        if line.timestamp:
            parts.append(line.timestamp.strftime(opts.timestamp_format))
        else:
            parts.append("(no timestamp)")
    parts.append(line.message)
    return opts.separator.join(parts)


def format_lines(lines: List[LogLine], options: Optional[FormatOptions] = None) -> List[str]:
    return [format_line(line, options) for line in lines]

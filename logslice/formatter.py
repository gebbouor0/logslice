"""Format log lines for display with configurable options."""
from dataclasses import dataclass
from typing import List, Optional
from logslice.parser import LogLine


@dataclass
class FormatOptions:
    show_line_numbers: bool = True
    show_timestamps: bool = True
    timestamp_format: str = "%Y-%m-%d %H:%M:%S"
    separator: str = " | "
    max_message_length: Optional[int] = None


def format_line(line: LogLine, options: Optional[FormatOptions] = None) -> str:
    opts = options or FormatOptions()
    parts = []

    if opts.show_line_numbers:
        parts.append(f"[{line.line_number}]")

    if opts.show_timestamps:
        if line.timestamp is not None:
            parts.append(line.timestamp.strftime(opts.timestamp_format))
        else:
            parts.append("(no timestamp)")

    msg = line.message
    if opts.max_message_length and len(msg) > opts.max_message_length:
        msg = msg[: opts.max_message_length] + "..."
    parts.append(msg)

    return opts.separator.join(parts)


def format_lines(lines: List[LogLine], options: Optional[FormatOptions] = None) -> List[str]:
    return [format_line(line, options) for line in lines]

"""Formatting utilities for log lines."""
from dataclasses import dataclass
from typing import List, Optional
from logslice.parser import LogLine


@dataclass
class FormatOptions:
    show_line_number: bool = True
    show_timestamp: bool = True
    timestamp_format: str = "%Y-%m-%dT%H:%M:%S"
    separator: str = " | "
    max_message_length: Optional[int] = None


def format_line(line: LogLine, options: Optional[FormatOptions] = None) -> str:
    opts = options or FormatOptions()
    parts: List[str] = []

    if opts.show_line_number and line.line_number is not None:
        parts.append(f"[{line.line_number}]")

    if opts.show_timestamp:
        if line.timestamp:
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

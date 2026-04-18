"""Line formatting with configurable options."""
from dataclasses import dataclass
from typing import List, Optional
from logslice.parser import LogLine


@dataclass
class FormatOptions:
    show_line_number: bool = True
    show_timestamp: bool = True
    timestamp_format: str = "%Y-%m-%d %H:%M:%S"
    prefix: str = ""
    max_message_length: Optional[int] = None
    ellipsis: str = "..."


def format_line(line: LogLine, opts: Optional[FormatOptions] = None) -> str:
    if opts is None:
        opts = FormatOptions()

    parts = []

    if opts.prefix:
        parts.append(opts.prefix)

    if opts.show_line_number:
        parts.append(f"[{line.line_number}]")

    if opts.show_timestamp:
        if line.timestamp is not None:
            parts.append(line.timestamp.strftime(opts.timestamp_format))
        else:
            parts.append("(no timestamp)")

    msg = line.message
    if opts.max_message_length is not None and len(msg) > opts.max_message_length:
        msg = msg[:opts.max_message_length] + opts.ellipsis

    parts.append(msg)
    return " ".join(parts)


def format_lines(lines: List[LogLine], opts: Optional[FormatOptions] = None) -> List[str]:
    return [format_line(line, opts) for line in lines]

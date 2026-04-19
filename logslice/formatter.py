from dataclasses import dataclass
from typing import List, Optional
from logslice.parser import LogLine


@dataclass
class FormatOptions:
    show_line_numbers: bool = True
    show_timestamps: bool = True
    timestamp_format: str = "%Y-%m-%d %H:%M:%S"
    separator: str = " | "


def format_line(log_line: LogLine, options: Optional[FormatOptions] = None) -> str:
    if options is None:
        options = FormatOptions()

    parts = []

    if options.show_line_numbers and log_line.line_number is not None:
        parts.append(f"#{log_line.line_number}")

    if options.show_timestamps:
        if log_line.timestamp is not None:
            parts.append(log_line.timestamp.strftime(options.timestamp_format))
        else:
            parts.append("(no timestamp)")

    parts.append(log_line.message)

    return options.separator.join(parts)


def format_lines(log_lines: List[LogLine], options: Optional[FormatOptions] = None) -> List[str]:
    return [format_line(line, options) for line in log_lines]

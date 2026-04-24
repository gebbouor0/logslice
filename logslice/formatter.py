"""formatter.py — simple line-level formatting helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

from logslice.parser import LogLine


@dataclass
class FormatOptions:
    show_line_number: bool = True
    show_timestamp: bool = True
    show_level: bool = True
    timestamp_fmt: str = "%Y-%m-%d %H:%M:%S"
    separator: str = " | "


def format_line(line: LogLine, opts: FormatOptions | None = None) -> str:
    if opts is None:
        opts = FormatOptions()

    parts: List[str] = []

    if opts.show_line_number:
        parts.append(f"[{line.line_number}]")

    if opts.show_timestamp:
        ts = (
            line.timestamp.strftime(opts.timestamp_fmt)
            if line.timestamp
            else "-"
        )
        parts.append(ts)

    if opts.show_level:
        parts.append(line.level or "-")

    parts.append(line.message)
    return opts.separator.join(parts)


def format_lines(
    lines: Iterable[LogLine],
    opts: FormatOptions | None = None,
) -> List[str]:
    return [format_line(line, opts) for line in lines]

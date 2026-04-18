"""Normalize log line messages: strip whitespace, collapse spaces, etc."""
from dataclasses import dataclass
from typing import List, Optional
import re

from logslice.parser import LogLine


@dataclass
class NormalizedLine:
    original: LogLine
    normalized_message: str

    @property
    def raw(self) -> str:
        return self.original.raw

    @property
    def line_number(self) -> Optional[int]:
        return self.original.line_number


def normalize_message(
    message: str,
    collapse_whitespace: bool = True,
    strip: bool = True,
    lowercase: bool = False,
    remove_ansi: bool = True,
) -> str:
    if remove_ansi:
        message = re.sub(r"\x1b\[[0-9;]*m", "", message)
    if strip:
        message = message.strip()
    if collapse_whitespace:
        message = re.sub(r"[ \t]+", " ", message)
    if lowercase:
        message = message.lower()
    return message


def normalize_line(
    line: LogLine,
    collapse_whitespace: bool = True,
    strip: bool = True,
    lowercase: bool = False,
    remove_ansi: bool = True,
) -> NormalizedLine:
    msg = normalize_message(
        line.message,
        collapse_whitespace=collapse_whitespace,
        strip=strip,
        lowercase=lowercase,
        remove_ansi=remove_ansi,
    )
    return NormalizedLine(original=line, normalized_message=msg)


def normalize_lines(
    lines: List[LogLine],
    collapse_whitespace: bool = True,
    strip: bool = True,
    lowercase: bool = False,
    remove_ansi: bool = True,
) -> List[NormalizedLine]:
    return [
        normalize_line(l, collapse_whitespace, strip, lowercase, remove_ansi)
        for l in lines
    ]

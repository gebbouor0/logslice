"""Strip ANSI escape codes and control characters from log messages."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional

from logslice.parser import LogLine

_ANSI_ESCAPE = re.compile(r"\x1b\[[0-9;]*[mABCDEFGHJKLMnsuhl]", re.ASCII)
_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]")


@dataclass(frozen=True)
class StrippedLine:
    _line: LogLine
    message: str
    was_changed: bool

    @property
    def raw(self) -> str:
        return self._line.raw

    @property
    def line_number(self) -> int:
        return self._line.line_number

    @property
    def timestamp(self):
        return self._line.timestamp

    @property
    def level(self) -> Optional[str]:
        return self._line.level


def strip_message(
    message: str,
    remove_ansi: bool = True,
    remove_control: bool = True,
) -> str:
    """Return message with ANSI codes and/or control characters removed."""
    result = message
    if remove_ansi:
        result = _ANSI_ESCAPE.sub("", result)
    if remove_control:
        result = _CONTROL_CHARS.sub("", result)
    return result


def strip_line(
    line: LogLine,
    remove_ansi: bool = True,
    remove_control: bool = True,
) -> StrippedLine:
    """Strip a single LogLine, returning a StrippedLine."""
    cleaned = strip_message(line.message, remove_ansi=remove_ansi, remove_control=remove_control)
    return StrippedLine(
        _line=line,
        message=cleaned,
        was_changed=(cleaned != line.message),
    )


@dataclass
class StripResult:
    lines: List[StrippedLine]
    total_changed: int

    def __len__(self) -> int:
        return len(self.lines)


def strip_lines(
    lines: List[LogLine],
    remove_ansi: bool = True,
    remove_control: bool = True,
) -> StripResult:
    """Strip all lines and return a StripResult."""
    stripped = [
        strip_line(line, remove_ansi=remove_ansi, remove_control=remove_control)
        for line in lines
    ]
    changed = sum(1 for s in stripped if s.was_changed)
    return StripResult(lines=stripped, total_changed=changed)

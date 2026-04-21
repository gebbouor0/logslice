"""capper.py — cap log lines by field value length or message length."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from logslice.parser import LogLine


@dataclass
class CappedLine:
    line: LogLine
    original_message: str
    capped: bool

    @property
    def raw(self) -> str:
        return self.line.raw

    @property
    def line_number(self) -> Optional[int]:
        return self.line.line_number

    @property
    def message(self) -> str:
        return self.line.message


@dataclass
class CapResult:
    items: List[CappedLine] = field(default_factory=list)
    total_input: int = 0
    total_capped: int = 0

    def __len__(self) -> int:
        return len(self.items)

    @property
    def capped_ratio(self) -> float:
        if self.total_input == 0:
            return 0.0
        return self.total_capped / self.total_input


def cap_message(message: str, max_length: int, ellipsis: str = "...") -> tuple[str, bool]:
    """Truncate message to max_length chars. Returns (new_message, was_capped)."""
    if max_length < 0:
        raise ValueError("max_length must be >= 0")
    if len(message) <= max_length:
        return message, False
    cut = max(0, max_length - len(ellipsis))
    return message[:cut] + ellipsis, True


def cap_lines(
    lines: List[LogLine],
    max_length: int,
    ellipsis: str = "...",
) -> CapResult:
    """Cap message length for each log line."""
    result = CapResult(total_input=len(lines))
    for log in lines:
        new_msg, was_capped = cap_message(log.message, max_length, ellipsis)
        if was_capped:
            capped_log = LogLine(
                raw=log.raw,
                timestamp=log.timestamp,
                message=new_msg,
                line_number=log.line_number,
            )
            result.total_capped += 1
        else:
            capped_log = log
        result.items.append(
            CappedLine(line=capped_log, original_message=log.message, capped=was_capped)
        )
    return result


def format_capped(result: CapResult) -> List[str]:
    """Return formatted messages from a CapResult."""
    return [item.message for item in result.items]

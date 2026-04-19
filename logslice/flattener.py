"""Flatten nested/multiline log entries into single LogLine objects."""
from dataclasses import dataclass, field
from typing import List, Optional
from logslice.parser import LogLine


@dataclass
class FlattenedLine:
    _line: LogLine
    continuation_count: int = 0
    joined_message: str = ""

    @property
    def raw(self) -> str:
        return self._line.raw

    @property
    def line_number(self) -> Optional[int]:
        return self._line.line_number

    def as_log_line(self) -> LogLine:
        result = LogLine(
            raw=self.raw,
            timestamp=self._line.timestamp,
            level=self._line.level,
            message=self.joined_message or self._line.message,
            line_number=self._line.line_number,
        )
        return result


def _is_continuation(line: LogLine) -> bool:
    """A line is a continuation if it has no timestamp and starts with whitespace or common prefixes."""
    if line.timestamp is not None:
        return False
    raw = line.raw
    return bool(raw) and (raw[0] in (" ", "\t") or raw.startswith("...") or raw.startswith("|"))


def flatten_lines(lines: List[LogLine], separator: str = " ") -> List[FlattenedLine]:
    """Merge continuation lines into the preceding primary log line."""
    result: List[FlattenedLine] = []
    current: Optional[FlattenedLine] = None

    for line in lines:
        if _is_continuation(line) and current is not None:
            current.joined_message = (current.joined_message + separator + line.raw.strip()).strip()
            current.continuation_count += 1
        else:
            if current is not None:
                result.append(current)
            current = FlattenedLine(
                _line=line,
                continuation_count=0,
                joined_message=line.message or "",
            )

    if current is not None:
        result.append(current)

    return result


def format_flattened(entries: List[FlattenedLine]) -> List[str]:
    out = []
    for entry in entries:
        suffix = f" [+{entry.continuation_count} lines]" if entry.continuation_count else ""
        out.append(f"{entry.joined_message}{suffix}")
    return out

"""Build a positional index of log lines for fast lookup by line number or timestamp."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from logslice.parser import LogLine


@dataclass
class LogIndex:
    by_line: Dict[int, LogLine] = field(default_factory=dict)
    by_minute: Dict[str, List[LogLine]] = field(default_factory=dict)

    def __len__(self) -> int:
        return len(self.by_line)

    def get(self, line_number: int) -> Optional[LogLine]:
        return self.by_line.get(line_number)

    def get_by_minute(self, minute_key: str) -> List[LogLine]:
        return self.by_minute.get(minute_key, [])


def _minute_key(ts: datetime) -> str:
    return ts.strftime("%Y-%m-%dT%H:%M")


def build_index(lines: List[LogLine]) -> LogIndex:
    index = LogIndex()
    for line in lines:
        if line.line_number is not None:
            index.by_line[line.line_number] = line
        if line.timestamp is not None:
            key = _minute_key(line.timestamp)
            index.by_minute.setdefault(key, []).append(line)
    return index


def lookup_range(index: LogIndex, start: int, end: int) -> List[LogLine]:
    """Return lines whose line_number falls in [start, end] inclusive."""
    return [index.by_line[n] for n in range(start, end + 1) if n in index.by_line]

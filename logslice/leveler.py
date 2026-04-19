"""Level-based filtering and elevation of log lines."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from logslice.parser import LogLine

LEVEL_ORDER = {"debug": 0, "info": 1, "warning": 2, "warn": 2, "error": 3, "critical": 4, "fatal": 4}


@dataclass
class LeveledLine:
    log_line: LogLine
    level: str

    @property
    def raw(self) -> str:
        return self.log_line.raw

    @property
    def line_number(self) -> int:
        return self.log_line.line_number


@dataclass
class LevelResult:
    lines: List[LeveledLine] = field(default_factory=list)
    dropped: int = 0

    def __len__(self) -> int:
        return len(self.lines)


def _extract_level(line: LogLine) -> str:
    msg = line.message.lower()
    for lvl in ("critical", "fatal", "error", "warning", "warn", "info", "debug"):
        if lvl in msg:
            return lvl
    return "info"


def filter_by_level(lines: List[LogLine], min_level: str) -> LevelResult:
    """Keep only lines at or above min_level."""
    min_rank = LEVEL_ORDER.get(min_level.lower(), 0)
    result = LevelResult()
    for line in lines:
        lvl = _extract_level(line)
        rank = LEVEL_ORDER.get(lvl, 1)
        if rank >= min_rank:
            result.lines.append(LeveledLine(log_line=line, level=lvl))
        else:
            result.dropped += 1
    return result


def format_leveled(result: LevelResult) -> List[str]:
    return [f"[{ll.level.upper()}] {ll.raw}" for ll in result.lines]

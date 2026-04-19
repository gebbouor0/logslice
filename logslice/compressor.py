"""Compressor: run-length encode repeated log messages."""
from dataclasses import dataclass, field
from typing import List, Optional
from logslice.parser import LogLine
from datetime import datetime


@dataclass
class CompressedLine:
    log_line: LogLine
    count: int = 1
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None

    @property
    def raw(self) -> str:
        return self.log_line.raw

    @property
    def line_number(self) -> Optional[int]:
        return self.log_line.line_number


@dataclass
class CompressResult:
    lines: List[CompressedLine] = field(default_factory=list)

    @property
    def total_input(self) -> int:
        return sum(c.count for c in self.lines)

    @property
    def total_output(self) -> int:
        return len(self.lines)

    @property
    def ratio(self) -> float:
        if self.total_output == 0:
            return 1.0
        return self.total_input / self.total_output


def compress_lines(lines: List[LogLine]) -> CompressResult:
    """Run-length encode consecutive duplicate messages."""
    result = CompressResult()
    if not lines:
        return result

    current = CompressedLine(
        log_line=lines[0],
        count=1,
        first_seen=lines[0].timestamp,
        last_seen=lines[0].timestamp,
    )

    for line in lines[1:]:
        if line.message == current.log_line.message:
            current.count += 1
            current.last_seen = line.timestamp
        else:
            result.lines.append(current)
            current = CompressedLine(
                log_line=line,
                count=1,
                first_seen=line.timestamp,
                last_seen=line.timestamp,
            )

    result.lines.append(current)
    return result


def format_compressed(result: CompressResult) -> List[str]:
    out = []
    for c in result.lines:
        if c.count > 1:
            out.append(f"[x{c.count}] {c.log_line.message}")
        else:
            out.append(c.log_line.message)
    return out

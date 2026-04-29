"""Seeker: scan a log stream and jump to lines matching a search term."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Optional

from logslice.parser import LogLine


@dataclass
class SeekHit:
    line: LogLine
    context_before: List[LogLine] = field(default_factory=list)
    context_after: List[LogLine] = field(default_factory=list)

    @property
    def raw(self) -> str:
        return self.line.raw

    @property
    def line_number(self) -> Optional[int]:
        return self.line.line_number


@dataclass
class SeekResult:
    hits: List[SeekHit]
    total_input: int
    term: str

    def __len__(self) -> int:
        return len(self.hits)

    @property
    def hit_count(self) -> int:
        return len(self.hits)


def seek_lines(
    lines: List[LogLine],
    predicate: Callable[[LogLine], bool],
    term: str = "",
    before: int = 0,
    after: int = 0,
) -> SeekResult:
    """Find all lines matching *predicate*, optionally capturing surrounding context."""
    before = max(0, before)
    after = max(0, after)
    hits: List[SeekHit] = []
    for idx, line in enumerate(lines):
        if predicate(line):
            ctx_before = lines[max(0, idx - before): idx]
            ctx_after = lines[idx + 1: idx + 1 + after]
            hits.append(SeekHit(line=line, context_before=list(ctx_before), context_after=list(ctx_after)))
    return SeekResult(hits=hits, total_input=len(lines), term=term)


def format_seek_result(result: SeekResult) -> List[str]:
    """Render each hit with optional context into human-readable strings."""
    output: List[str] = []
    for hit in result.hits:
        for cl in hit.context_before:
            ts = cl.timestamp.isoformat() if cl.timestamp else "-"
            output.append(f"  [{cl.line_number}] {ts} | {cl.message}")
        ts = hit.line.timestamp.isoformat() if hit.line.timestamp else "-"
        output.append(f">> [{hit.line_number}] {ts} | {hit.line.message}")
        for cl in hit.context_after:
            ts = cl.timestamp.isoformat() if cl.timestamp else "-"
            output.append(f"  [{cl.line_number}] {ts} | {cl.message}")
        if hit.context_before or hit.context_after:
            output.append("---")
    return output

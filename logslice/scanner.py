"""Scanner: search log lines for pattern matches and return match metadata."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional, Sequence

from logslice.parser import LogLine


@dataclass
class ScanMatch:
    line: LogLine
    pattern: str
    spans: List[tuple]  # list of (start, end) match positions in message

    @property
    def raw(self) -> str:
        return self.line.raw

    @property
    def line_number(self) -> Optional[int]:
        return self.line.line_number

    @property
    def match_count(self) -> int:
        return len(self.spans)


@dataclass
class ScanResult:
    pattern: str
    matches: List[ScanMatch] = field(default_factory=list)
    total_input: int = 0

    @property
    def total_matches(self) -> int:
        return len(self.matches)

    @property
    def hit_rate(self) -> float:
        if self.total_input == 0:
            return 0.0
        return self.total_matches / self.total_input


def scan_lines(
    lines: Sequence[LogLine],
    pattern: str,
    case_sensitive: bool = False,
) -> ScanResult:
    """Scan lines for regex pattern, returning match metadata for each hit."""
    flags = 0 if case_sensitive else re.IGNORECASE
    try:
        compiled = re.compile(pattern, flags)
    except re.error as exc:
        raise ValueError(f"Invalid pattern {pattern!r}: {exc}") from exc

    result = ScanResult(pattern=pattern, total_input=len(lines))
    for line in lines:
        msg = line.message or ""
        spans = [m.span() for m in compiled.finditer(msg)]
        if spans:
            result.matches.append(ScanMatch(line=line, pattern=pattern, spans=spans))
    return result


def format_scan(result: ScanResult) -> List[str]:
    """Format scan results as human-readable lines."""
    out: List[str] = [
        f"Pattern : {result.pattern}",
        f"Scanned : {result.total_input}",
        f"Matches : {result.total_matches} ({result.hit_rate:.1%})",
        "-" * 40,
    ]
    for m in result.matches:
        prefix = f"[{m.line_number}]" if m.line_number is not None else "[-]"
        out.append(f"{prefix} ({m.match_count}x) {m.raw}")
    return out

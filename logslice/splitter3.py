"""splitter3 — split log lines into segments by keyword boundaries."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Optional

from logslice.parser import LogLine


@dataclass
class KeywordSegment:
    name: str
    lines: List[LogLine] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.lines)


@dataclass
class KeywordSplitResult:
    segments: List[KeywordSegment] = field(default_factory=list)
    total_input: int = 0

    def __len__(self) -> int:
        return len(self.segments)

    @property
    def total_lines(self) -> int:
        return sum(len(s) for s in self.segments)


def split_by_keyword(
    lines: List[LogLine],
    keywords: List[str],
    *,
    case_sensitive: bool = False,
    include_boundary: bool = True,
    default_name: str = "preamble",
) -> KeywordSplitResult:
    """Split *lines* into segments each time a keyword is encountered."""
    result = KeywordSplitResult(total_input=len(lines))
    if not lines:
        return result

    current_segment = KeywordSegment(name=default_name)

    def _matches(msg: str) -> Optional[str]:
        cmp = msg if case_sensitive else msg.lower()
        for kw in keywords:
            needle = kw if case_sensitive else kw.lower()
            if needle in cmp:
                return kw
        return None

    for line in lines:
        hit = _matches(line.message)
        if hit is not None:
            if current_segment.lines or result.segments:
                result.segments.append(current_segment)
            current_segment = KeywordSegment(name=hit)
            if include_boundary:
                current_segment.lines.append(line)
        else:
            current_segment.lines.append(line)

    if current_segment.lines:
        result.segments.append(current_segment)

    return result


def format_keyword_segments(result: KeywordSplitResult) -> List[str]:
    out: List[str] = []
    for seg in result.segments:
        out.append(f"=== {seg.name} ({len(seg)} lines) ===")
        for line in seg.lines:
            out.append(f"  [{line.line_number}] {line.message}")
    return out

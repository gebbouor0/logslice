"""Split log lines into named segments based on delimiter patterns."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import re
from logslice.parser import LogLine


@dataclass
class Segment:
    name: str
    lines: List[LogLine] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.lines)


def split_by_pattern(
    lines: List[LogLine],
    pattern: str,
    default_name: str = "default",
) -> List[Segment]:
    """Split lines into segments each time *pattern* matches a line's message.

    The matching line becomes the first line of the new segment.
    Lines before the first match go into a segment named *default_name*.
    """
    regex = re.compile(pattern)
    segments: List[Segment] = []
    current: Segment = Segment(name=default_name)

    for line in lines:
        if regex.search(line.message):
            if current.lines or segments:
                segments.append(current)
            current = Segment(name=line.message[:60].strip())
        current.lines.append(line)

    if current.lines:
        segments.append(current)

    return segments


def split_by_size(lines: List[LogLine], size: int) -> List[Segment]:
    """Split lines into fixed-size segments."""
    if size < 1:
        raise ValueError("size must be >= 1")
    segments = []
    for i in range(0, len(lines), size):
        chunk = lines[i : i + size]
        name = f"segment-{i // size + 1}"
        segments.append(Segment(name=name, lines=chunk))
    return segments


def format_segments(segments: List[Segment], separator: str = "---") -> List[str]:
    """Render segments as labelled text blocks."""
    out: List[str] = []
    for seg in segments:
        out.append(f"{separator} [{seg.name}] ({len(seg)} lines) {separator}")
        for line in seg.lines:
            out.append(line.raw)
    return out

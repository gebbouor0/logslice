"""Log rotation detector: identifies log rotation boundaries in a stream."""
from dataclasses import dataclass, field
from typing import List, Optional
from logslice.parser import LogLine


@dataclass
class RotationSegment:
    index: int
    lines: List[LogLine] = field(default_factory=list)
    reason: str = ""

    def __len__(self) -> int:
        return len(self.lines)


def _is_rotation_boundary(prev: LogLine, curr: LogLine) -> bool:
    """Detect rotation: timestamp goes backwards or line number resets."""
    if prev.timestamp and curr.timestamp:
        if curr.timestamp < prev.timestamp:
            return True
    if prev.line_number is not None and curr.line_number is not None:
        if curr.line_number < prev.line_number:
            return True
    return False


def detect_rotations(
    lines: List[LogLine],
    detect_timestamp_reset: bool = True,
    detect_line_number_reset: bool = True,
) -> List[RotationSegment]:
    """Split lines into segments separated by detected rotation boundaries."""
    if not lines:
        return []

    segments: List[RotationSegment] = []
    current = RotationSegment(index=0)
    current.lines.append(lines[0])

    for i in range(1, len(lines)):
        prev, curr = lines[i - 1 = ""
        if detect_timestamp_reset and prev.timestamp and curr.timestamp:
            if curr.timestamp < prev.timestamp:
                reason = "timestamp_reset"
        if not reason and detect_line_number_reset:
            if prev.line_number is not None and curr.line_number is not None:
                if curr.line_number < prev.line_number:
                    reason = "line_number_reset"
        if reason:
            current.reason = reason
            segments.append(current)
            current = RotationSegment(index=len(segments))
        current.lines.append(curr)

    segments.append(current)
    return segments


def format_rotations(segments: List[RotationSegment]) -> List[str]:
    out: List[str] = []
    for seg in segments:
        header = f"=== Segment {seg.index}"
        if seg.reason:
            header += f" (rotation: {seg.reason})"
        header += f" — {len(seg)} lines ==="
        out.append(header)
        for line in seg.lines:
            out.append(line.raw)
    return out

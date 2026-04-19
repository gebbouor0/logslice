"""Align log lines from multiple sources to a common time grid."""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from logslice.parser import LogLine


@dataclass
class AlignedSlot:
    bucket: datetime
    lines: List[LogLine] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.lines)


def align_lines(
    lines: List[LogLine],
    interval_seconds: int = 60,
) -> List[AlignedSlot]:
    """Group lines into fixed-width time buckets."""
    if interval_seconds <= 0:
        raise ValueError("interval_seconds must be positive")

    slots: Dict[datetime, AlignedSlot] = {}
    delta = timedelta(seconds=interval_seconds)

    for line in lines:
        if line.timestamp is None:
            continue
        ts = line.timestamp
        bucket = datetime(
            ts.year, ts.month, ts.day,
            ts.hour, ts.minute,
            (ts.second // interval_seconds) * interval_seconds,
        )
        if bucket not in slots:
            slots[bucket] = AlignedSlot(bucket=bucket)
        slots[bucket].lines.append(line)

    return [slots[k] for k in sorted(slots)]


def format_aligned(slots: List[AlignedSlot], show_empty: bool = False) -> str:
    """Render aligned slots as a readable string."""
    parts: List[str] = []
    for slot in slots:
        if not slot.lines and not show_empty:
            continue
        header = f"[{slot.bucket.isoformat()}] ({len(slot.lines)} lines)"
        parts.append(header)
        for line in slot.lines:
            parts.append(f"  {line.message}")
    return "\n".join(parts)

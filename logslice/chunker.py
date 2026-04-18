"""Split log lines into time-based chunks."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional

from logslice.parser import LogLine


@dataclass
class Chunk:
    index: int
    start: Optional[datetime]
    end: Optional[datetime]
    lines: List[LogLine] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.lines)


def chunk_by_size(lines: List[LogLine], size: int) -> List[Chunk]:
    """Split lines into fixed-size chunks."""
    if size <= 0:
        raise ValueError("Chunk size must be positive")
    chunks = []
    for i in range(0, len(lines), size):
        batch = lines[i : i + size]
        timestamps = [l.timestamp for l in batch if l.timestamp]
        start = min(timestamps) if timestamps else None
        end = max(timestamps) if timestamps else None
        chunks.append(Chunk(index=len(chunks), start=start, end=end, lines=batch))
    return chunks


def chunk_by_interval(lines: List[LogLine], interval: timedelta) -> List[Chunk]:
    """Split lines into time-based interval chunks."""
    if not lines:
        return []

    chunks: List[Chunk] = []
    current: List[LogLine] = []
    bucket_start: Optional[datetime] = None

    for line in lines:
        if line.timestamp is None:
            current.append(line)
            continue

        if bucket_start is None:
            bucket_start = line.timestamp

        if line.timestamp >= bucket_start + interval:
            if current:
                timestamps = [l.timestamp for l in current if l.timestamp]
                chunks.append(Chunk(
                    index=len(chunks),
                    start=min(timestamps) if timestamps else None,
                    end=max(timestamps) if timestamps else None,
                    lines=current,
                ))
            current = [line]
            bucket_start = line.timestamp
        else:
            current.append(line)

    if current:
        timestamps = [l.timestamp for l in current if l.timestamp]
        chunks.append(Chunk(
            index=len(chunks),
            start=min(timestamps) if timestamps else None,
            end=max(timestamps) if timestamps else None,
            lines=current,
        ))

    return chunks

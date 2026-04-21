"""Schedule future replay or processing of log lines based on timestamps."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Iterable, Optional

from logslice.parser import LogLine


@dataclass
class ScheduledItem:
    line: LogLine
    fire_at: datetime  # absolute wall-clock time to process this line
    offset_seconds: float  # offset from schedule anchor

    @property
    def raw(self) -> str:
        return self.line.raw


@dataclass
class Schedule:
    items: list[ScheduledItem] = field(default_factory=list)
    anchor: Optional[datetime] = None  # wall-clock anchor for the first event
    skipped: int = 0

    def __len__(self) -> int:
        return len(self.items)

    def is_empty(self) -> bool:
        return len(self.items) == 0


def build_schedule(
    lines: Iterable[LogLine],
    anchor: Optional[datetime] = None,
    speed: float = 1.0,
) -> Schedule:
    """Map log timestamps to wall-clock fire times.

    Args:
        lines: Log lines with timestamps.
        anchor: Wall-clock time for the first event; defaults to now.
        speed: Playback speed multiplier.

    Returns:
        Schedule with fire_at times for each timestamped line.
    """
    if speed <= 0:
        raise ValueError("speed must be positive")

    anchor = anchor or datetime.now(tz=timezone.utc)
    schedule = Schedule(anchor=anchor)

    first_ts: Optional[datetime] = None

    for line in lines:
        if line.timestamp is None:
            schedule.skipped += 1
            continue

        if first_ts is None:
            first_ts = line.timestamp

        raw_offset = (line.timestamp - first_ts).total_seconds()
        scaled_offset = raw_offset / speed
        fire_at = anchor + timedelta(seconds=scaled_offset)

        schedule.items.append(
            ScheduledItem(line=line, fire_at=fire_at, offset_seconds=scaled_offset)
        )

    return schedule


def items_due_by(schedule: Schedule, cutoff: datetime) -> list[ScheduledItem]:
    """Return all items whose fire_at is <= cutoff."""
    return [item for item in schedule.items if item.fire_at <= cutoff]

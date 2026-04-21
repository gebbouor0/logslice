"""Replay log lines with simulated timing based on original timestamps."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Callable, Iterable, Iterator, Optional

from logslice.parser import LogLine


@dataclass
class ReplayEvent:
    line: LogLine
    delay_seconds: float  # delay from previous event
    elapsed_seconds: float  # total elapsed from replay start

    @property
    def raw(self) -> str:
        return self.line.raw

    @property
    def line_number(self) -> Optional[int]:
        return self.line.line_number


@dataclass
class ReplayResult:
    events: list[ReplayEvent] = field(default_factory=list)
    skipped: int = 0

    def __len__(self) -> int:
        return len(self.events)


def build_replay(
    lines: Iterable[LogLine],
    speed: float = 1.0,
    max_gap_seconds: Optional[float] = None,
) -> ReplayResult:
    """Build a replay sequence from log lines, computing inter-event delays.

    Args:
        lines: Input log lines (must have timestamps for timing).
        speed: Playback multiplier (2.0 = twice as fast, 0.5 = half speed).
        max_gap_seconds: Cap any single gap to this many seconds (real time).

    Returns:
        ReplayResult with events and count of skipped (no-timestamp) lines.
    """
    if speed <= 0:
        raise ValueError("speed must be positive")

    result = ReplayResult()
    prev_ts: Optional[datetime] = None
    elapsed = 0.0

    for line in lines:
        if line.timestamp is None:
            result.skipped += 1
            continue

        if prev_ts is None:
            delay = 0.0
        else:
            raw_gap = (line.timestamp - prev_ts).total_seconds()
            raw_gap = max(raw_gap, 0.0)  # guard against backwards timestamps
            delay = raw_gap / speed
            if max_gap_seconds is not None:
                delay = min(delay, max_gap_seconds)

        elapsed += delay
        result.events.append(ReplayEvent(line=line, delay_seconds=delay, elapsed_seconds=elapsed))
        prev_ts = line.timestamp

    return result


def replay_lines(
    result: ReplayResult,
    callback: Callable[[ReplayEvent], None],
    *,
    live: bool = False,
) -> None:
    """Iterate replay events, optionally sleeping between them."""
    for event in result.events:
        if live and event.delay_seconds > 0:
            time.sleep(event.delay_seconds)
        callback(event)

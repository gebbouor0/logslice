"""Limit log lines by head/tail count or by time window."""
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime, timedelta
from logslice.parser import LogLine


@dataclass
class LimitResult:
    lines: List[LogLine]
    total_input: int
    dropped: int
    strategy: str

    def __len__(self) -> int:
        return len(self.lines)


def limit_head(lines: List[LogLine], n: int) -> LimitResult:
    """Keep only the first n lines."""
    if n < 0:
        raise ValueError("n must be >= 0")
    kept = lines[:n]
    return LimitResult(
        lines=kept,
        total_input=len(lines),
        dropped=len(lines) - len(kept),
        strategy="head",
    )


def limit_tail(lines: List[LogLine], n: int) -> LimitResult:
    """Keep only the last n lines."""
    if n < 0:
        raise ValueError("n must be >= 0")
    kept = lines[-n:] if n > 0 else []
    return LimitResult(
        lines=kept,
        total_input=len(lines),
        dropped=len(lines) - len(kept),
        strategy="tail",
    )


def limit_by_duration(
    lines: List[LogLine], seconds: float, from_end: bool = False
) -> LimitResult:
    """Keep lines within `seconds` of the first (or last) timestamp found."""
    if seconds < 0:
        raise ValueError("seconds must be >= 0")
    timestamped = [l for l in lines if l.timestamp is not None]
    if not timestamped:
        return LimitResult(lines=list(lines), total_input=len(lines), dropped=0, strategy="duration")

    delta = timedelta(seconds=seconds)
    if from_end:
        anchor = timestamped[-1].timestamp
        kept = [l for l in lines if l.timestamp is None or (anchor - l.timestamp) <= delta]
    else:
        anchor = timestamped[0].timestamp
        kept = [l for l in lines if l.timestamp is None or (l.timestamp - anchor) <= delta]

    return LimitResult(
        lines=kept,
        total_input=len(lines),
        dropped=len(lines) - len(kept),
        strategy="duration",
    )


def limit_lines(
    lines: List[LogLine],
    strategy: str = "head",
    n: int = 100,
    seconds: Optional[float] = None,
    from_end: bool = False,
) -> LimitResult:
    if strategy == "head":
        return limit_head(lines, n)
    elif strategy == "tail":
        return limit_tail(lines, n)
    elif strategy == "duration":
        if seconds is None:
            raise ValueError("seconds required for duration strategy")
        return limit_by_duration(lines, seconds, from_end=from_end)
    else:
        raise ValueError(f"Unknown strategy: {strategy}")

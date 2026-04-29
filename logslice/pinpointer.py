"""Pinpointer: locate lines nearest to a target timestamp or line number."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from logslice.parser import LogLine


@dataclass
class PinResult:
    target_ts: Optional[datetime]
    target_line_number: Optional[int]
    nearest: Optional[LogLine]
    distance_seconds: Optional[float]  # None when matching by line number
    distance_lines: Optional[int]      # None when matching by timestamp
    total_input: int

    @property
    def found(self) -> bool:
        return self.nearest is not None


def pinpoint_by_timestamp(lines: List[LogLine], target: datetime) -> PinResult:
    """Return the line whose timestamp is closest to *target*."""
    candidates = [l for l in lines if l.timestamp is not None]
    if not candidates:
        return PinResult(
            target_ts=target,
            target_line_number=None,
            nearest=None,
            distance_seconds=None,
            distance_lines=None,
            total_input=len(lines),
        )
    best = min(candidates, key=lambda l: abs((l.timestamp - target).total_seconds()))
    dist = abs((best.timestamp - target).total_seconds())
    return PinResult(
        target_ts=target,
        target_line_number=None,
        nearest=best,
        distance_seconds=dist,
        distance_lines=None,
        total_input=len(lines),
    )


def pinpoint_by_line_number(lines: List[LogLine], target: int) -> PinResult:
    """Return the line whose line_number is closest to *target*."""
    if not lines:
        return PinResult(
            target_ts=None,
            target_line_number=target,
            nearest=None,
            distance_seconds=None,
            distance_lines=None,
            total_input=0,
        )
    best = min(lines, key=lambda l: abs((l.line_number or 0) - target))
    dist = abs((best.line_number or 0) - target)
    return PinResult(
        target_ts=None,
        target_line_number=target,
        nearest=best,
        distance_seconds=None,
        distance_lines=dist,
        total_input=len(lines),
    )


def format_pin_result(result: PinResult) -> str:
    if not result.found:
        return "pinpointer: no matching line found"
    line = result.nearest
    ts_str = line.timestamp.isoformat() if line.timestamp else "-"
    if result.distance_seconds is not None:
        dist = f"distance={result.distance_seconds:.3f}s"
    else:
        dist = f"distance={result.distance_lines} lines"
    return f"[{line.line_number}] {ts_str} | {line.message}  ({dist})"

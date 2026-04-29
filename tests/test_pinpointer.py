"""Tests for logslice.pinpointer."""
from datetime import datetime, timezone
from typing import Optional

import pytest

from logslice.parser import LogLine
from logslice.pinpointer import (
    PinResult,
    format_pin_result,
    pinpoint_by_line_number,
    pinpoint_by_timestamp,
)


def dt(hour: int, minute: int = 0, second: int = 0) -> datetime:
    return datetime(2024, 1, 1, hour, minute, second, tzinfo=timezone.utc)


def make_line(
    msg: str,
    line_number: int = 1,
    timestamp: Optional[datetime] = None,
) -> LogLine:
    return LogLine(
        raw=msg,
        message=msg,
        timestamp=timestamp,
        level=None,
        line_number=line_number,
    )


# --- pinpoint_by_timestamp ---

def test_pinpoint_ts_returns_nearest():
    lines = [
        make_line("a", 1, dt(10, 0, 0)),
        make_line("b", 2, dt(10, 0, 5)),
        make_line("c", 3, dt(10, 0, 20)),
    ]
    result = pinpoint_by_timestamp(lines, dt(10, 0, 6))
    assert result.nearest.message == "b"
    assert result.distance_seconds == pytest.approx(1.0)


def test_pinpoint_ts_exact_match():
    lines = [make_line("exact", 1, dt(12, 0, 0))]
    result = pinpoint_by_timestamp(lines, dt(12, 0, 0))
    assert result.distance_seconds == pytest.approx(0.0)
    assert result.nearest.message == "exact"


def test_pinpoint_ts_no_timestamps_returns_not_found():
    lines = [make_line("no-ts", 1, None)]
    result = pinpoint_by_timestamp(lines, dt(9, 0, 0))
    assert not result.found
    assert result.nearest is None


def test_pinpoint_ts_empty_input():
    result = pinpoint_by_timestamp([], dt(9, 0, 0))
    assert not result.found
    assert result.total_input == 0


def test_pinpoint_ts_sets_total_input():
    lines = [make_line("x", i, dt(10, i % 60)) for i in range(5)]
    result = pinpoint_by_timestamp(lines, dt(10, 2))
    assert result.total_input == 5


# --- pinpoint_by_line_number ---

def test_pinpoint_ln_returns_nearest():
    lines = [make_line("a", 1), make_line("b", 5), make_line("c", 10)]
    result = pinpoint_by_line_number(lines, 4)
    assert result.nearest.message == "b"
    assert result.distance_lines == 1


def test_pinpoint_ln_exact_match():
    lines = [make_line("hit", 7)]
    result = pinpoint_by_line_number(lines, 7)
    assert result.distance_lines == 0
    assert result.nearest.message == "hit"


def test_pinpoint_ln_empty_input():
    result = pinpoint_by_line_number([], 3)
    assert not result.found
    assert result.total_input == 0


def test_pinpoint_ln_distance_lines_not_none():
    lines = [make_line("z", 100)]
    result = pinpoint_by_line_number(lines, 1)
    assert result.distance_seconds is None
    assert result.distance_lines == 99


# --- format_pin_result ---

def test_format_found_by_ts():
    line = make_line("hello", 3, dt(10, 5, 0))
    result = PinResult(
        target_ts=dt(10, 5, 2),
        target_line_number=None,
        nearest=line,
        distance_seconds=2.0,
        distance_lines=None,
        total_input=10,
    )
    out = format_pin_result(result)
    assert "hello" in out
    assert "2.000s" in out


def test_format_not_found():
    result = PinResult(
        target_ts=dt(10, 0, 0),
        target_line_number=None,
        nearest=None,
        distance_seconds=None,
        distance_lines=None,
        total_input=0,
    )
    out = format_pin_result(result)
    assert "no matching" in out

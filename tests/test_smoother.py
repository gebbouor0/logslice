"""Tests for logslice.smoother."""
from datetime import datetime, timedelta
from typing import Optional

import pytest

from logslice.parser import LogLine
from logslice.smoother import SmoothedLine, SmoothResult, smooth_lines, format_smoothed


def make_line(
    message: str,
    ts: Optional[datetime] = None,
    line_number: int = 1,
) -> LogLine:
    return LogLine(
        raw=message,
        timestamp=ts,
        message=message,
        level=None,
        line_number=line_number,
    )


def dt(hour: int, minute: int = 0, second: int = 0) -> datetime:
    return datetime(2024, 1, 1, hour, minute, second)


def test_smooth_empty_input():
    result = smooth_lines([], max_gap=timedelta(minutes=1))
    assert len(result) == 0
    assert result.interpolated_count == 0


def test_smooth_no_gap_below_threshold():
    lines = [
        make_line("a", dt(10, 0, 0), 1),
        make_line("b", dt(10, 0, 30), 2),
    ]
    result = smooth_lines(lines, max_gap=timedelta(minutes=1))
    assert len(result) == 2
    assert result.interpolated_count == 0
    assert result.original_count == 2


def test_smooth_inserts_gap_marker():
    lines = [
        make_line("a", dt(10, 0, 0), 1),
        make_line("b", dt(10, 5, 0), 2),
    ]
    result = smooth_lines(lines, max_gap=timedelta(minutes=1))
    assert len(result) == 3
    assert result.interpolated_count == 1
    assert result.original_count == 2


def test_smooth_gap_marker_midpoint_timestamp():
    lines = [
        make_line("a", dt(10, 0, 0), 1),
        make_line("b", dt(10, 10, 0), 2),
    ]
    result = smooth_lines(lines, max_gap=timedelta(minutes=1))
    gap = [sl for sl in result.lines if sl.interpolated][0]
    assert gap.timestamp == datetime(2024, 1, 1, 10, 5, 0)


def test_smooth_custom_fill_message():
    lines = [
        make_line("x", dt(9, 0, 0), 1),
        make_line("y", dt(9, 2, 0), 2),
    ]
    result = smooth_lines(lines, max_gap=timedelta(seconds=30), fill_message="--- gap ---")
    gap = [sl for sl in result.lines if sl.interpolated][0]
    assert gap.log_line.message == "--- gap ---"


def test_smooth_skips_none_timestamps():
    lines = [
        make_line("a", dt(10, 0, 0), 1),
        make_line("b", None, 2),
        make_line("c", dt(10, 30, 0), 3),
    ]
    # Gap between line 1 and 3 is huge but line 2 has no timestamp so gap check
    # only fires when both prev and current have timestamps.
    result = smooth_lines(lines, max_gap=timedelta(minutes=1))
    # gap inserted between line 2 (no-ts, prev_ts stays at 10:00) and line 3
    assert result.interpolated_count == 1


def test_smooth_multiple_gaps():
    lines = [
        make_line("a", dt(10, 0), 1),
        make_line("b", dt(10, 5), 2),
        make_line("c", dt(10, 10), 3),
    ]
    result = smooth_lines(lines, max_gap=timedelta(minutes=1))
    assert result.interpolated_count == 2


def test_format_smoothed_marks_interpolated():
    lines = [
        make_line("start", dt(8, 0), 1),
        make_line("end", dt(8, 10), 2),
    ]
    result = smooth_lines(lines, max_gap=timedelta(minutes=1))
    formatted = format_smoothed(result)
    assert any(line.startswith("~") for line in formatted)
    assert any(line.startswith(" ") for line in formatted)

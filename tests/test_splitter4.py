"""Tests for logslice.splitter4."""
from datetime import datetime, timedelta
from typing import Optional

import pytest

from logslice.parser import LogLine
from logslice.splitter4 import (
    TimedSegment,
    TimedSplitResult,
    split_by_line_count,
    split_by_duration,
    format_segments,
)


def make_line(msg: str, ts: Optional[datetime] = None, n: int = 1) -> LogLine:
    return LogLine(raw=msg, message=msg, timestamp=ts, line_number=n)


def dt(offset: int) -> datetime:
    return datetime(2024, 1, 1, 12, 0, 0) + timedelta(seconds=offset)


# --- split_by_line_count ---

def test_split_by_line_count_basic():
    lines = [make_line(f"msg{i}", n=i) for i in range(6)]
    result = split_by_line_count(lines, 2)
    assert len(result) == 3
    assert all(len(s) == 2 for s in result.segments)


def test_split_by_line_count_remainder():
    lines = [make_line(f"msg{i}", n=i) for i in range(5)]
    result = split_by_line_count(lines, 2)
    assert len(result) == 3
    assert len(result.segments[-1]) == 1


def test_split_by_line_count_total_input():
    lines = [make_line(f"m{i}", n=i) for i in range(7)]
    result = split_by_line_count(lines, 3)
    assert result.total_input == 7
    assert result.total_lines == 7


def test_split_by_line_count_timestamps():
    lines = [make_line(f"m{i}", ts=dt(i * 10), n=i) for i in range(4)]
    result = split_by_line_count(lines, 2)
    assert result.segments[0].start_time == dt(0)
    assert result.segments[0].end_time == dt(10)
    assert result.segments[1].start_time == dt(20)


def test_split_by_line_count_invalid():
    with pytest.raises(ValueError):
        split_by_line_count([], 0)


def test_split_by_line_count_empty():
    result = split_by_line_count([], 3)
    assert len(result) == 0
    assert result.total_input == 0


# --- split_by_duration ---

def test_split_by_duration_basic():
    lines = [
        make_line("a", ts=dt(0), n=1),
        make_line("b", ts=dt(5), n=2),
        make_line("c", ts=dt(15), n=3),
    ]
    result = split_by_duration(lines, 10)
    assert len(result) == 2
    assert len(result.segments[0]) == 2
    assert len(result.segments[1]) == 1


def test_split_by_duration_skips_no_timestamp():
    lines = [
        make_line("a", ts=dt(0), n=1),
        make_line("no-ts", ts=None, n=2),
        make_line("b", ts=dt(5), n=3),
    ]
    result = split_by_duration(lines, 20)
    assert result.skipped == 1
    assert result.total_lines == 2


def test_split_by_duration_invalid():
    with pytest.raises(ValueError):
        split_by_duration([], 0)


def test_split_by_duration_empty():
    result = split_by_duration([], 60)
    assert len(result) == 0
    assert result.total_input == 0


# --- format_segments ---

def test_format_segments_non_empty():
    lines = [make_line(f"m{i}", ts=dt(i * 5), n=i) for i in range(4)]
    result = split_by_line_count(lines, 2)
    out = format_segments(result)
    assert len(out) == 2
    assert "segment 0" in out[0]
    assert "lines=2" in out[0]


def test_format_segments_no_timestamp_shows_dash():
    lines = [make_line("x", ts=None, n=1), make_line("y", ts=None, n=2)]
    result = split_by_line_count(lines, 2)
    out = format_segments(result)
    assert "—" in out[0]

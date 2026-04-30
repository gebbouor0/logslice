"""Tests for logslice.slicer."""
from datetime import datetime, timedelta
from typing import Optional

import pytest

from logslice.parser import LogLine
from logslice.slicer import Slice, SliceResult, slice_by_index, slice_by_timestamp, format_slice


def make_line(msg: str, ts: Optional[datetime] = None, n: int = 1) -> LogLine:
    return LogLine(raw=msg, message=msg, timestamp=ts, line_number=n)


def dt(offset: int) -> datetime:
    return datetime(2024, 3, 1, 8, 0, 0) + timedelta(seconds=offset)


# --- slice_by_index ---

def test_slice_by_index_basic():
    lines = [make_line(f"m{i}", n=i) for i in range(10)]
    result = slice_by_index(lines, 2, 5)
    assert len(result.slices[0]) == 3


def test_slice_by_index_default_end():
    lines = [make_line(f"m{i}", n=i) for i in range(5)]
    result = slice_by_index(lines, 1)
    assert len(result.slices[0]) == 4


def test_slice_by_index_clamps_negative_start():
    lines = [make_line(f"m{i}", n=i) for i in range(4)]
    result = slice_by_index(lines, -5, 2)
    assert len(result.slices[0]) == 2


def test_slice_by_index_total_input():
    lines = [make_line(f"m{i}", n=i) for i in range(8)]
    result = slice_by_index(lines, 0, 4)
    assert result.total_input == 8


def test_slice_by_index_label():
    lines = [make_line("x", n=1)]
    result = slice_by_index(lines, 0, 1, label="my-slice")
    assert result.slices[0].label == "my-slice"


def test_slice_by_index_empty_range():
    lines = [make_line(f"m{i}", n=i) for i in range(5)]
    result = slice_by_index(lines, 3, 3)
    assert result.slices[0].is_empty


# --- slice_by_timestamp ---

def test_slice_by_timestamp_basic():
    lines = [make_line(f"m{i}", ts=dt(i * 10), n=i) for i in range(5)]
    result = slice_by_timestamp(lines, start=dt(10), end=dt(30))
    assert len(result.slices[0]) == 3


def test_slice_by_timestamp_no_bounds_keeps_all_with_ts():
    lines = [
        make_line("a", ts=dt(0), n=1),
        make_line("b", ts=None, n=2),
        make_line("c", ts=dt(20), n=3),
    ]
    result = slice_by_timestamp(lines)
    assert len(result.slices[0]) == 2


def test_slice_by_timestamp_no_match_empty_slice():
    lines = [make_line("a", ts=dt(0), n=1)]
    result = slice_by_timestamp(lines, start=dt(100), end=dt(200))
    assert result.slices[0].is_empty


def test_slice_by_timestamp_total_input():
    lines = [make_line(f"m{i}", ts=dt(i), n=i) for i in range(6)]
    result = slice_by_timestamp(lines, start=dt(2), end=dt(4))
    assert result.total_input == 6


# --- format_slice ---

def test_format_slice_non_empty():
    lines = [make_line("hello", ts=dt(0), n=1)]
    result = slice_by_index(lines, 0, 1, label="test")
    out = format_slice(result)
    assert any("test" in l for l in out)
    assert any("hello" in l for l in out)


def test_format_slice_no_timestamp_shows_dash():
    lines = [make_line("msg", ts=None, n=1)]
    result = slice_by_index(lines, 0, 1)
    out = format_slice(result)
    assert any("—" in l for l in out)

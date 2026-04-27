"""Tests for logslice.cutter."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

import pytest

from logslice.parser import LogLine
from logslice.cutter import cut_lines, format_cut, CutResult


def make_line(n: int, msg: str = "hello", ts: Optional[datetime] = None) -> LogLine:
    return LogLine(raw=msg, line_number=n, timestamp=ts, message=msg)


def make_lines(count: int) -> list:
    return [make_line(i + 1, f"msg {i + 1}") for i in range(count)]


def test_cut_basic_slice():
    lines = make_lines(10)
    result = cut_lines(lines, start=2, end=5)
    assert len(result) == 3
    assert result.lines[0].message == "msg 3"
    assert result.lines[-1].message == "msg 5"


def test_cut_no_args_returns_all():
    lines = make_lines(5)
    result = cut_lines(lines)
    assert len(result) == 5
    assert result.total_input == 5


def test_cut_start_only():
    lines = make_lines(8)
    result = cut_lines(lines, start=5)
    assert len(result) == 3
    assert result.lines[0].message == "msg 6"


def test_cut_end_only():
    lines = make_lines(8)
    result = cut_lines(lines, end=3)
    assert len(result) == 3
    assert result.lines[-1].message == "msg 3"


def test_cut_negative_start():
    lines = make_lines(10)
    result = cut_lines(lines, start=-3)
    assert len(result) == 3
    assert result.lines[0].message == "msg 8"


def test_cut_negative_end():
    lines = make_lines(10)
    result = cut_lines(lines, start=0, end=-2)
    assert len(result) == 8


def test_cut_empty_input():
    result = cut_lines([])
    assert len(result) == 0
    assert result.total_input == 0


def test_cut_out_of_range_end():
    lines = make_lines(4)
    result = cut_lines(lines, start=0, end=100)
    assert len(result) == 4


def test_cut_dropped_head():
    lines = make_lines(10)
    result = cut_lines(lines, start=3, end=7)
    assert result.dropped_head == 3


def test_cut_dropped_tail():
    lines = make_lines(10)
    result = cut_lines(lines, start=3, end=7)
    assert result.dropped_tail == 3


def test_cut_total_input_preserved():
    lines = make_lines(20)
    result = cut_lines(lines, start=5, end=15)
    assert result.total_input == 20


def test_format_cut_basic():
    lines = make_lines(3)
    result = cut_lines(lines)
    formatted = format_cut(result)
    assert len(formatted) == 3
    assert "msg 1" in formatted[0]


def test_format_cut_with_timestamp():
    ts = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    lines = [make_line(1, "hello ts", ts=ts)]
    result = cut_lines(lines)
    formatted = format_cut(result)
    assert "2024-01-01" in formatted[0]


def test_format_cut_no_timestamp_shows_dash():
    lines = [make_line(1, "no ts")]
    result = cut_lines(lines)
    formatted = format_cut(result)
    assert "- " in formatted[0] or "-" in formatted[0]

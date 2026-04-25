"""Tests for logslice.peeker."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

import pytest

from logslice.parser import LogLine
from logslice.peeker import PeekResult, PeekWindow, format_peek, peek_lines


def make_line(n: int, msg: str, ts: Optional[datetime] = None) -> LogLine:
    return LogLine(raw=msg, line_number=n, timestamp=ts, message=msg)


def is_error(line: LogLine) -> bool:
    return "ERROR" in line.message


# ---------------------------------------------------------------------------
# peek_lines — basic behaviour
# ---------------------------------------------------------------------------

def test_peek_no_matches_returns_empty():
    lines = [make_line(i, f"INFO msg {i}") for i in range(5)]
    result = peek_lines(lines, is_error, before=1, after=1)
    assert len(result) == 0
    assert result.total_input == 5


def test_peek_single_match_centre():
    lines = [
        make_line(1, "INFO a"),
        make_line(2, "INFO b"),
        make_line(3, "ERROR boom"),
        make_line(4, "INFO c"),
        make_line(5, "INFO d"),
    ]
    result = peek_lines(lines, is_error, before=2, after=2)
    assert len(result) == 1
    w = result.windows[0]
    assert w.line.line_number == 3
    assert [l.line_number for l in w.before] == [1, 2]
    assert [l.line_number for l in w.after] == [4, 5]


def test_peek_clamps_at_stream_start():
    lines = [
        make_line(1, "ERROR first"),
        make_line(2, "INFO a"),
        make_line(3, "INFO b"),
    ]
    result = peek_lines(lines, is_error, before=3, after=1)
    w = result.windows[0]
    assert w.before == []  # nothing before index 0
    assert len(w.after) == 1


def test_peek_clamps_at_stream_end():
    lines = [
        make_line(1, "INFO a"),
        make_line(2, "INFO b"),
        make_line(3, "ERROR last"),
    ]
    result = peek_lines(lines, is_error, before=1, after=5)
    w = result.windows[0]
    assert len(w.before) == 1
    assert w.after == []


def test_peek_multiple_matches():
    lines = [
        make_line(1, "ERROR one"),
        make_line(2, "INFO mid"),
        make_line(3, "ERROR two"),
    ]
    result = peek_lines(lines, is_error, before=0, after=0)
    assert len(result) == 2
    assert result.windows[0].line_number == 1
    assert result.windows[1].line_number == 3


def test_peek_empty_input():
    result = peek_lines([], is_error)
    assert len(result) == 0
    assert result.total_input == 0


def test_peek_invalid_before_raises():
    with pytest.raises(ValueError):
        peek_lines([], is_error, before=-1)


def test_peek_invalid_after_raises():
    with pytest.raises(ValueError):
        peek_lines([], is_error, after=-1)


# ---------------------------------------------------------------------------
# format_peek
# ---------------------------------------------------------------------------

def test_format_peek_empty_result():
    result = PeekResult()
    assert format_peek(result) == []


def test_format_peek_match_line_prefixed():
    lines = [
        make_line(1, "INFO before"),
        make_line(2, "ERROR boom"),
        make_line(3, "INFO after"),
    ]
    result = peek_lines(lines, is_error, before=1, after=1)
    output = format_peek(result)
    match_row = [r for r in output if r.startswith(">>")]
    assert len(match_row) == 1
    assert "ERROR boom" in match_row[0]


def test_format_peek_separator_between_windows():
    lines = [
        make_line(1, "ERROR a"),
        make_line(2, "INFO gap"),
        make_line(3, "ERROR b"),
    ]
    result = peek_lines(lines, is_error, before=0, after=0)
    output = format_peek(result, separator="---")
    assert "---" in output

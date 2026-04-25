"""Tests for logslice/cursor.py"""
import pytest
from datetime import datetime, timezone
from logslice.parser import LogLine
from logslice.cursor import (
    Cursor,
    CursorResult,
    seek_cursor,
    reset_cursor,
    format_cursor,
)


def make_line(n: int, ts: datetime | None = None, msg: str = "msg") -> LogLine:
    return LogLine(raw=f"line {n}", line_number=n, timestamp=ts, message=msg)


def dt(hour: int = 0, minute: int = 0) -> datetime:
    return datetime(2024, 1, 1, hour, minute, tzinfo=timezone.utc)


def test_cursor_initial_state():
    c = Cursor(name="main")
    assert c.position == 0
    assert c.last_timestamp is None
    assert c.last_line_number is None
    assert c.is_at_start()


def test_seek_cursor_basic():
    lines = [make_line(i) for i in range(5)]
    c = Cursor(name="main")
    result = seek_cursor(lines, c, 3)
    assert len(result.consumed) == 3
    assert len(result.remaining) == 2
    assert c.position == 3


def test_seek_cursor_updates_last_line_number():
    lines = [make_line(i) for i in range(5)]
    c = Cursor(name="main")
    seek_cursor(lines, c, 4)
    assert c.last_line_number == 3


def test_seek_cursor_updates_last_timestamp():
    lines = [
        make_line(0, ts=dt(10, 0)),
        make_line(1, ts=dt(10, 5)),
        make_line(2, ts=None),
    ]
    c = Cursor(name="ts-test")
    seek_cursor(lines, c, 3)
    assert c.last_timestamp == dt(10, 5)


def test_seek_cursor_beyond_end_clamps():
    lines = [make_line(i) for i in range(3)]
    c = Cursor(name="main")
    result = seek_cursor(lines, c, 100)
    assert len(result.consumed) == 3
    assert len(result.remaining) == 0
    assert c.position == 3


def test_seek_cursor_zero_count():
    lines = [make_line(i) for i in range(3)]
    c = Cursor(name="main")
    result = seek_cursor(lines, c, 0)
    assert len(result.consumed) == 0
    assert len(result.remaining) == 3
    assert c.is_at_start()


def test_seek_cursor_invalid_count():
    lines = [make_line(i) for i in range(3)]
    c = Cursor(name="main")
    with pytest.raises(ValueError):
        seek_cursor(lines, c, -1)


def test_seek_cursor_sequential_calls():
    lines = [make_line(i) for i in range(6)]
    c = Cursor(name="main")
    r1 = seek_cursor(lines, c, 2)
    r2 = seek_cursor(lines, c, 2)
    assert [l.line_number for l in r1.consumed] == [0, 1]
    assert [l.line_number for l in r2.consumed] == [2, 3]
    assert c.position == 4


def test_reset_cursor():
    lines = [make_line(i, ts=dt(0, i)) for i in range(4)]
    c = Cursor(name="main")
    seek_cursor(lines, c, 4)
    assert c.position == 4
    reset_cursor(c)
    assert c.position == 0
    assert c.last_timestamp is None
    assert c.last_line_number is None


def test_cursor_result_len():
    lines = [make_line(i) for i in range(5)]
    c = Cursor(name="main")
    result = seek_cursor(lines, c, 3)
    assert len(result) == 3


def test_format_cursor_no_timestamp():
    c = Cursor(name="demo")
    out = format_cursor(c)
    assert "demo" in out
    assert "pos=0" in out
    assert "last_ts=-" in out


def test_format_cursor_with_timestamp():
    lines = [make_line(1, ts=dt(9, 30))]
    c = Cursor(name="demo")
    seek_cursor(lines, c, 1)
    out = format_cursor(c)
    assert "09:30" in out
    assert "pos=1" in out

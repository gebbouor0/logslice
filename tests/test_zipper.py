import pytest
from datetime import datetime, timezone
from logslice.parser import LogLine
from logslice.zipper import zip_by_index, zip_by_timestamp, format_zipped


def dt(offset_seconds: int):
    return datetime(2024, 1, 1, 0, 0, offset_seconds, tzinfo=timezone.utc)


def make_line(msg: str, ts=None, n: int = 1) -> LogLine:
    return LogLine(raw=msg, message=msg, timestamp=ts, line_number=n)


def test_zip_by_index_equal_length():
    left = [make_line("a"), make_line("b")]
    right = [make_line("x"), make_line("y")]
    rows = zip_by_index(left, right)
    assert len(rows) == 2
    assert rows[0].left_message == "a"
    assert rows[0].right_message == "x"


def test_zip_by_index_left_longer():
    left = [make_line("a"), make_line("b"), make_line("c")]
    right = [make_line("x")]
    rows = zip_by_index(left, right)
    assert len(rows) == 3
    assert rows[1].right is None
    assert rows[1].right_message == ""


def test_zip_by_index_right_longer():
    left = [make_line("a")]
    right = [make_line("x"), make_line("y")]
    rows = zip_by_index(left, right)
    assert len(rows) == 2
    assert rows[1].left is None


def test_zip_by_index_empty():
    rows = zip_by_index([], [])
    assert rows == []


def test_zip_by_timestamp_basic():
    left = [make_line("a", ts=dt(0)), make_line("b", ts=dt(10))]
    right = [make_line("x", ts=dt(1)), make_line("y", ts=dt(11))]
    rows = zip_by_timestamp(left, right)
    assert len(rows) == 2
    assert rows[0].left_message == "a"
    assert rows[0].right_message == "x"
    assert rows[1].left_message == "b"
    assert rows[1].right_message == "y"


def test_zip_by_timestamp_unmatched_right():
    left = [make_line("a", ts=dt(0))]
    right = [make_line("x", ts=dt(0)), make_line("extra", ts=dt(50))]
    rows = zip_by_timestamp(left, right)
    lefts = [r for r in rows if r.left is not None]
    extras = [r for r in rows if r.left is None]
    assert len(lefts) == 1
    assert len(extras) == 1
    assert extras[0].right_message == "extra"


def test_zip_by_timestamp_no_timestamps():
    left = [make_line("a"), make_line("b")]
    right = [make_line("x")]
    rows = zip_by_timestamp(left, right)
    assert rows == []


def test_format_zipped_header():
    left = [make_line("hello")]
    right = [make_line("world")]
    rows = zip_by_index(left, right)
    lines = format_zipped(rows, width=10)
    assert lines[0].startswith("LEFT")
    assert "RIGHT" in lines[0]


def test_format_zipped_content():
    left = [make_line("hello")]
    right = [make_line("world")]
    rows = zip_by_index(left, right)
    lines = format_zipped(rows, width=10)
    assert "hello" in lines[2]
    assert "world" in lines[2]

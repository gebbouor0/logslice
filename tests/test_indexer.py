import pytest
from datetime import datetime, timezone
from logslice.parser import LogLine
from logslice.indexer import build_index, lookup_range, _minute_key


def make_line(n: int, ts=None, msg="hello") -> LogLine:
    return LogLine(raw=f"line {n}", message=msg, timestamp=ts, line_number=n)


def dt(h: int, m: int) -> datetime:
    return datetime(2024, 1, 1, h, m, 0, tzinfo=timezone.utc)


def test_build_index_len():
    lines = [make_line(i) for i in range(1, 6)]
    idx = build_index(lines)
    assert len(idx) == 5


def test_get_by_line_number():
    lines = [make_line(i) for i in range(1, 4)]
    idx = build_index(lines)
    assert idx.get(2).line_number == 2


def test_get_missing_returns_none():
    idx = build_index([])
    assert idx.get(99) is None


def test_index_by_minute_groups_correctly():
    lines = [
        make_line(1, dt(10, 5)),
        make_line(2, dt(10, 5)),
        make_line(3, dt(10, 6)),
    ]
    idx = build_index(lines)
    assert len(idx.get_by_minute("2024-01-01T10:05")) == 2
    assert len(idx.get_by_minute("2024-01-01T10:06")) == 1


def test_get_by_minute_missing_key():
    idx = build_index([])
    assert idx.get_by_minute("2024-01-01T00:00") == []


def test_no_timestamp_not_in_minute_index():
    lines = [make_line(1, None)]
    idx = build_index(lines)
    assert len(idx.by_minute) == 0


def test_no_line_number_not_in_line_index():
    line = LogLine(raw="x", message="x", timestamp=None, line_number=None)
    idx = build_index([line])
    assert len(idx) == 0


def test_lookup_range_basic():
    lines = [make_line(i) for i in range(1, 6)]
    idx = build_index(lines)
    result = lookup_range(idx, 2, 4)
    assert [l.line_number for l in result] == [2, 3, 4]


def test_lookup_range_partial():
    lines = [make_line(i) for i in range(1, 4)]
    idx = build_index(lines)
    result = lookup_range(idx, 2, 10)
    assert [l.line_number for l in result] == [2, 3]


def test_lookup_range_empty():
    idx = build_index([])
    assert lookup_range(idx, 1, 5) == []

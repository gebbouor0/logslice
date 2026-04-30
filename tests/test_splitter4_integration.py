"""Integration tests combining split_by_line_count and split_by_duration."""
from datetime import datetime, timedelta
from typing import Optional

from logslice.parser import LogLine
from logslice.splitter4 import split_by_line_count, split_by_duration, format_segments


def make_line(msg: str, ts: Optional[datetime] = None, n: int = 1) -> LogLine:
    return LogLine(raw=msg, message=msg, timestamp=ts, line_number=n)


def dt(offset: int) -> datetime:
    return datetime(2024, 6, 1, 0, 0, 0) + timedelta(seconds=offset)


def _make_lines(n: int, interval: int = 10) -> list:
    return [make_line(f"line {i}", ts=dt(i * interval), n=i + 1) for i in range(n)]


def test_line_count_total_lines_preserved():
    lines = _make_lines(20)
    result = split_by_line_count(lines, 4)
    total = sum(len(s) for s in result.segments)
    assert total == 20


def test_duration_split_all_into_one_with_large_window():
    lines = _make_lines(10, interval=5)
    result = split_by_duration(lines, 9999)
    assert len(result) == 1
    assert len(result.segments[0]) == 10


def test_duration_split_each_line_own_segment():
    lines = _make_lines(5, interval=100)
    result = split_by_duration(lines, 1)
    assert len(result) == 5


def test_format_segments_count_matches_segment_count():
    lines = _make_lines(9)
    result = split_by_line_count(lines, 3)
    out = format_segments(result)
    assert len(out) == len(result.segments)


def test_split_by_duration_segment_indices_sequential():
    lines = _make_lines(6, interval=20)
    result = split_by_duration(lines, 15)
    for i, seg in enumerate(result.segments):
        assert seg.index == i

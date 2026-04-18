"""Tests for logslice.chunker."""

from datetime import datetime, timedelta

import pytest

from logslice.parser import LogLine
from logslice.chunker import chunk_by_size, chunk_by_interval, Chunk


def make_line(n: int, ts: datetime = None) -> LogLine:
    return LogLine(line_number=n, raw=f"line {n}", timestamp=ts, message=f"line {n}")


T0 = datetime(2024, 1, 1, 12, 0, 0)


def test_chunk_by_size_basic():
    lines = [make_line(i) for i in range(7)]
    chunks = chunk_by_size(lines, 3)
    assert len(chunks) == 3
    assert len(chunks[0]) == 3
    assert len(chunks[1]) == 3
    assert len(chunks[2]) == 1


def test_chunk_by_size_indices():
    lines = [make_line(i) for i in range(6)]
    chunks = chunk_by_size(lines, 2)
    assert [c.index for c in chunks] == [0, 1, 2]


def test_chunk_by_size_timestamps():
    lines = [
        make_line(0, T0),
        make_line(1, T0 + timedelta(minutes=1)),
        make_line(2, T0 + timedelta(minutes=2)),
    ]
    chunks = chunk_by_size(lines, 2)
    assert chunks[0].start == T0
    assert chunks[0].end == T0 + timedelta(minutes=1)
    assert chunks[1].start == T0 + timedelta(minutes=2)


def test_chunk_by_size_invalid():
    with pytest.raises(ValueError):
        chunk_by_size([], 0)


def test_chunk_by_size_empty():
    assert chunk_by_size([], 5) == []


def test_chunk_by_interval_basic():
    lines = [
        make_line(i, T0 + timedelta(minutes=i * 2))
        for i in range(6)
    ]
    chunks = chunk_by_interval(lines, timedelta(minutes=5))
    assert len(chunks) >= 2
    total = sum(len(c) for c in chunks)
    assert total == 6


def test_chunk_by_interval_empty():
    assert chunk_by_interval([], timedelta(minutes=5)) == []


def test_chunk_by_interval_no_timestamps():
    lines = [make_line(i) for i in range(4)]
    chunks = chunk_by_interval(lines, timedelta(minutes=1))
    assert len(chunks) == 1
    assert len(chunks[0]) == 4


def test_chunk_by_interval_single_bucket():
    lines = [
        make_line(i, T0 + timedelta(seconds=i * 10))
        for i in range(5)
    ]
    chunks = chunk_by_interval(lines, timedelta(minutes=10))
    assert len(chunks) == 1
    assert chunks[0].start == T0

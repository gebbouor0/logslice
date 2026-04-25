"""Tests for logslice/flusher.py"""
from datetime import datetime, timezone, timedelta
from typing import Optional

import pytest

from logslice.parser import LogLine
from logslice.flusher import (
    FlushBatch,
    FlushResult,
    flush_by_size,
    flush_by_interval,
    format_flush_summary,
)


def make_line(msg: str, ts: Optional[datetime] = None, n: int = 1) -> LogLine:
    return LogLine(raw=msg, message=msg, timestamp=ts, line_number=n)


def dt(offset_seconds: float = 0) -> datetime:
    base = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    return base + timedelta(seconds=offset_seconds)


# --- flush_by_size ---

def test_flush_by_size_basic():
    lines = [make_line(f"msg{i}", n=i) for i in range(5)]
    result = flush_by_size(lines, batch_size=2)
    assert len(result) == 3
    assert len(result.batches[0]) == 2
    assert len(result.batches[1]) == 2
    assert len(result.batches[2]) == 1


def test_flush_by_size_total_input():
    lines = [make_line(f"m{i}") for i in range(7)]
    result = flush_by_size(lines, batch_size=3)
    assert result.total_input == 7
    assert result.total_flushed == 7


def test_flush_by_size_exact_division():
    lines = [make_line(f"m{i}") for i in range(6)]
    result = flush_by_size(lines, batch_size=3)
    assert len(result) == 2


def test_flush_by_size_empty_input():
    result = flush_by_size([], batch_size=5)
    assert len(result) == 0
    assert result.total_input == 0
    assert result.total_flushed == 0


def test_flush_by_size_invalid_raises():
    with pytest.raises(ValueError):
        flush_by_size([], batch_size=0)


def test_flush_by_size_batch_indices():
    lines = [make_line(f"m{i}") for i in range(4)]
    result = flush_by_size(lines, batch_size=2)
    assert [b.index for b in result.batches] == [0, 1]


# --- flush_by_interval ---

def test_flush_by_interval_basic():
    lines = [
        make_line("a", dt(0)),
        make_line("b", dt(5)),
        make_line("c", dt(65)),
        make_line("d", dt(70)),
    ]
    result = flush_by_interval(lines, interval_seconds=60)
    assert len(result) == 2
    assert len(result.batches[0]) == 2
    assert len(result.batches[1]) == 2


def test_flush_by_interval_empty_input():
    result = flush_by_interval([], interval_seconds=30)
    assert len(result) == 0
    assert result.total_input == 0


def test_flush_by_interval_invalid_raises():
    with pytest.raises(ValueError):
        flush_by_interval([], interval_seconds=0)


def test_flush_by_interval_no_timestamps_all_in_one_batch():
    lines = [make_line(f"m{i}") for i in range(5)]
    result = flush_by_interval(lines, interval_seconds=10)
    assert len(result) == 1
    assert len(result.batches[0]) == 5


def test_flush_by_interval_start_end_time():
    lines = [
        make_line("x", dt(0)),
        make_line("y", dt(30)),
    ]
    result = flush_by_interval(lines, interval_seconds=60)
    b = result.batches[0]
    assert b.start_time == dt(0)
    assert b.end_time == dt(30)


def test_flush_by_interval_total_flushed():
    lines = [make_line(f"m{i}", dt(i * 10)) for i in range(10)]
    result = flush_by_interval(lines, interval_seconds=25)
    assert result.total_flushed == 10


# --- format_flush_summary ---

def test_format_flush_summary_contains_batch_count():
    lines = [make_line(f"m{i}", dt(i)) for i in range(3)]
    result = flush_by_size(lines, batch_size=2)
    summary = format_flush_summary(result)
    assert "2 batches" in summary


def test_format_flush_summary_no_error_on_empty():
    result = flush_by_size([], batch_size=5)
    summary = format_flush_summary(result)
    assert "0 batches" in summary

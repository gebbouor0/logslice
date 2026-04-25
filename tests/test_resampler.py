"""Tests for logslice.resampler."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from logslice.parser import LogLine
from logslice.resampler import (
    ResampledBucket,
    ResampleResult,
    resample_lines,
    format_resampled,
)


def make_line(msg: str, ts: datetime | None = None, n: int = 1) -> LogLine:
    return LogLine(raw=msg, line_number=n, timestamp=ts, level=None, message=msg)


def dt(h: int, m: int, s: int = 0) -> datetime:
    return datetime(2024, 1, 1, h, m, s, tzinfo=timezone.utc)


# --- basic behaviour ---

def test_resample_empty_input():
    result = resample_lines([], interval_seconds=60)
    assert len(result) == 0
    assert result.total_bucketed == 0
    assert result.skipped == 0


def test_resample_skips_no_timestamp():
    lines = [make_line("no ts", ts=None)]
    result = resample_lines(lines, interval_seconds=60)
    assert result.skipped == 1
    assert result.total_bucketed == 0


def test_resample_single_bucket():
    lines = [
        make_line("a", dt(10, 0, 0)),
        make_line("b", dt(10, 0, 30)),
    ]
    result = resample_lines(lines, interval_seconds=60)
    assert len(result) == 1
    assert result.total_bucketed == 2


def test_resample_two_buckets():
    lines = [
        make_line("a", dt(10, 0, 0)),
        make_line("b", dt(10, 1, 0)),
    ]
    result = resample_lines(lines, interval_seconds=60)
    assert len(result) == 2


def test_resample_bucket_label_format():
    lines = [make_line("x", dt(9, 5, 0))]
    result = resample_lines(lines, interval_seconds=60)
    assert result.buckets[0].label == "2024-01-01T09:05:00"


def test_resample_buckets_ordered():
    lines = [
        make_line("late", dt(10, 2, 0)),
        make_line("early", dt(10, 0, 0)),
    ]
    result = resample_lines(lines, interval_seconds=60)
    assert result.buckets[0].label < result.buckets[1].label


def test_resample_invalid_interval():
    with pytest.raises(ValueError):
        resample_lines([], interval_seconds=0)


def test_resample_bucket_start_end():
    lines = [
        make_line("first", dt(10, 0, 5)),
        make_line("last", dt(10, 0, 55)),
    ]
    result = resample_lines(lines, interval_seconds=60)
    b = result.buckets[0]
    assert b.start == dt(10, 0, 5)
    assert b.end == dt(10, 0, 55)


def test_resample_mixed_with_and_without_timestamps():
    lines = [
        make_line("no ts", None),
        make_line("has ts", dt(10, 0, 0)),
    ]
    result = resample_lines(lines, interval_seconds=60)
    assert result.skipped == 1
    assert result.total_bucketed == 1


def test_format_resampled_non_empty():
    lines = [make_line("x", dt(10, 0, 0))]
    result = resample_lines(lines, interval_seconds=60)
    rows = format_resampled(result)
    assert len(rows) == 1
    assert "2024-01-01T10:00:00" in rows[0]
    assert "60s" in rows[0]


def test_format_resampled_empty_shows_message():
    result = resample_lines([], interval_seconds=60)
    rows = format_resampled(result)
    assert len(rows) == 1
    assert "no buckets" in rows[0]

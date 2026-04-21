"""Tests for logslice.bucketer."""
import pytest
from datetime import datetime, timezone
from logslice.parser import LogLine
from logslice.bucketer import bucket_lines, format_buckets, BucketResult


def make_line(ts=None, msg="hello", ln=1):
    return LogLine(raw=msg, line_number=ln, timestamp=ts, message=msg)


def dt(h=0, m=0, s=0):
    return datetime(2024, 1, 1, h, m, s, tzinfo=timezone.utc)


def test_bucket_empty_input():
    result = bucket_lines([])
    assert len(result) == 0
    assert result.total_bucketed == 0
    assert result.skipped == 0


def test_bucket_skips_no_timestamp():
    lines = [make_line(ts=None), make_line(ts=None)]
    result = bucket_lines(lines)
    assert result.skipped == 2
    assert len(result) == 0


def test_bucket_single_line():
    lines = [make_line(ts=dt(0, 0, 0))]
    result = bucket_lines(lines, interval_seconds=60)
    assert len(result) == 1
    assert result.total_bucketed == 1


def test_bucket_groups_within_interval():
    lines = [
        make_line(ts=dt(0, 0, 0), ln=1),
        make_line(ts=dt(0, 0, 30), ln=2),
        make_line(ts=dt(0, 1, 0), ln=3),
    ]
    result = bucket_lines(lines, interval_seconds=60)
    assert len(result) == 2
    assert len(result.buckets[0]) == 2
    assert len(result.buckets[1]) == 1


def test_bucket_interval_seconds_respected():
    lines = [
        make_line(ts=dt(0, 0, 0), ln=1),
        make_line(ts=dt(0, 0, 10), ln=2),
        make_line(ts=dt(0, 0, 20), ln=3),
    ]
    result = bucket_lines(lines, interval_seconds=10)
    assert len(result) == 3


def test_bucket_start_end_correct():
    lines = [make_line(ts=dt(0, 0, 0))]
    result = bucket_lines(lines, interval_seconds=30)
    b = result.buckets[0]
    assert b.start == dt(0, 0, 0)
    assert b.end == dt(0, 0, 30)


def test_bucket_invalid_interval():
    with pytest.raises(ValueError):
        bucket_lines([], interval_seconds=0)
    with pytest.raises(ValueError):
        bucket_lines([], interval_seconds=-5)


def test_bucket_mixed_timestamps_and_none():
    lines = [
        make_line(ts=dt(0, 0, 0), ln=1),
        make_line(ts=None, ln=2),
        make_line(ts=dt(0, 0, 5), ln=3),
    ]
    result = bucket_lines(lines, interval_seconds=60)
    assert result.skipped == 1
    assert result.total_bucketed == 2


def test_format_buckets_empty():
    result = BucketResult(buckets=[], interval_seconds=60, skipped=0)
    out = format_buckets(result)
    assert "no bucketed" in out


def test_format_buckets_contains_label():
    lines = [make_line(ts=dt(0, 0, 0))]
    result = bucket_lines(lines, interval_seconds=60)
    out = format_buckets(result)
    assert "2024-01-01" in out
    assert "total:" in out


def test_bucket_label_format():
    lines = [make_line(ts=dt(3, 15, 0))]
    result = bucket_lines(lines, interval_seconds=60)
    assert "03:15:00" in result.buckets[0].label

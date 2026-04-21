"""Integration tests for bucketer working with parser output."""
from datetime import datetime, timezone
from logslice.parser import LogLine
from logslice.bucketer import bucket_lines


def dt(h=0, m=0, s=0):
    return datetime(2024, 6, 1, h, m, s, tzinfo=timezone.utc)


def make_line(ts, msg="msg", ln=1):
    return LogLine(raw=msg, line_number=ln, timestamp=ts, message=msg)


def test_bucket_preserves_line_order_within_bucket():
    lines = [
        make_line(ts=dt(0, 0, 5), msg="first", ln=1),
        make_line(ts=dt(0, 0, 55), msg="second", ln=2),
    ]
    result = bucket_lines(lines, interval_seconds=60)
    assert result.buckets[0].lines[0].message == "first"
    assert result.buckets[0].lines[1].message == "second"


def test_bucket_total_bucketed_plus_skipped_equals_input():
    lines = [
        make_line(ts=dt(0, 0, 0), ln=1),
        make_line(ts=None, ln=2),
        make_line(ts=dt(0, 1, 0), ln=3),
        make_line(ts=None, ln=4),
    ]
    result = bucket_lines(lines, interval_seconds=60)
    assert result.total_bucketed + result.skipped == len(lines)


def test_bucket_large_interval_collapses_all():
    lines = [make_line(ts=dt(0, m, 0), ln=m) for m in range(10)]
    result = bucket_lines(lines, interval_seconds=3600)
    assert len(result) == 1
    assert len(result.buckets[0]) == 10


def test_bucket_one_second_interval_each_in_own_bucket():
    lines = [make_line(ts=dt(0, 0, s), ln=s) for s in range(5)]
    result = bucket_lines(lines, interval_seconds=1)
    assert len(result) == 5
    for b in result.buckets:
        assert len(b) == 1


def test_bucket_result_len_matches_bucket_count():
    lines = [
        make_line(ts=dt(0, 0, 0), ln=1),
        make_line(ts=dt(0, 2, 0), ln=2),
        make_line(ts=dt(0, 4, 0), ln=3),
    ]
    result = bucket_lines(lines, interval_seconds=60)
    assert len(result) == len(result.buckets) == 3

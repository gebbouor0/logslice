# tests/test_trender.py
import pytest
from datetime import datetime, timezone
from logslice.parser import LogLine
from logslice.trender import (
    TrendPoint,
    TrendResult,
    build_trend,
    format_trend,
    _floor_to_interval,
)


def make_line(ts=None, msg="hello", ln=1):
    return LogLine(raw=msg, message=msg, timestamp=ts, line_number=ln)


def dt(h, m=0, s=0):
    return datetime(2024, 1, 1, h, m, s, tzinfo=timezone.utc)


def test_build_trend_empty():
    result = build_trend([])
    assert len(result) == 0
    assert result.total_lines == 0
    assert result.skipped == 0


def test_build_trend_skips_no_timestamp():
    lines = [make_line(ts=None) for _ in range(5)]
    result = build_trend(lines)
    assert result.skipped == 5
    assert result.total_lines == 0


def test_build_trend_single_bucket():
    lines = [
        make_line(ts=dt(10, 0, 0)),
        make_line(ts=dt(10, 0, 30)),
        make_line(ts=dt(10, 0, 59)),
    ]
    result = build_trend(lines, interval_seconds=60)
    assert len(result) == 1
    assert result.points[0].count == 3


def test_build_trend_multiple_buckets():
    lines = [
        make_line(ts=dt(10, 0, 0)),
        make_line(ts=dt(10, 1, 0)),
        make_line(ts=dt(10, 2, 0)),
    ]
    result = build_trend(lines, interval_seconds=60)
    assert len(result) == 3
    assert all(p.count == 1 for p in result.points)


def test_build_trend_buckets_sorted():
    lines = [
        make_line(ts=dt(10, 5, 0)),
        make_line(ts=dt(10, 1, 0)),
        make_line(ts=dt(10, 3, 0)),
    ]
    result = build_trend(lines, interval_seconds=60)
    starts = [p.bucket_start for p in result.points]
    assert starts == sorted(starts)


def test_build_trend_peak_and_trough():
    lines = [
        make_line(ts=dt(10, 0, 0)),
        make_line(ts=dt(10, 0, 10)),
        make_line(ts=dt(10, 0, 20)),
        make_line(ts=dt(10, 1, 0)),
    ]
    result = build_trend(lines, interval_seconds=60)
    assert result.peak is not None
    assert result.peak.count == 3
    assert result.trough is not None
    assert result.trough.count == 1


def test_build_trend_invalid_interval():
    with pytest.raises(ValueError):
        build_trend([], interval_seconds=0)
    with pytest.raises(ValueError):
        build_trend([], interval_seconds=-5)


def test_build_trend_total_lines():
    lines = [make_line(ts=dt(10, i % 3, 0)) for i in range(9)]
    result = build_trend(lines, interval_seconds=60)
    assert result.total_lines == 9


def test_trend_point_label_format():
    lines = [make_line(ts=dt(14, 30, 0))]
    result = build_trend(lines, interval_seconds=60)
    assert result.points[0].label == "2024-01-01 14:30:00"


def test_format_trend_empty():
    result = TrendResult(points=[])
    out = format_trend(result)
    assert "no trend data" in out


def test_format_trend_contains_labels():
    lines = [
        make_line(ts=dt(9, 0, 0)),
        make_line(ts=dt(9, 1, 0)),
    ]
    result = build_trend(lines, interval_seconds=60)
    out = format_trend(result)
    assert "2024-01-01 09:00:00" in out
    assert "2024-01-01 09:01:00" in out


def test_format_trend_bar_present():
    lines = [make_line(ts=dt(10, 0, 0)) for _ in range(5)]
    result = build_trend(lines, interval_seconds=60)
    out = format_trend(result)
    assert "#" in out


def test_floor_to_interval_basic():
    ts = dt(10, 3, 45)
    floored = _floor_to_interval(ts, 60)
    assert floored == dt(10, 3, 0)


def test_floor_to_interval_five_minutes():
    ts = dt(10, 7, 30)
    floored = _floor_to_interval(ts, 300)
    assert floored == dt(10, 5, 0)

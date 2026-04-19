"""Tests for logslice.timeline."""
import pytest
from datetime import datetime, timezone
from logslice.parser import LogLine
from logslice.timeline import build_timeline, format_timeline, TimelineBucket


def dt(h: int, m: int, s: int = 0) -> datetime:
    return datetime(2024, 1, 1, h, m, s, tzinfo=timezone.utc)


def make_line(ts, msg="msg", n=1):
    return LogLine(raw=msg, line_number=n, timestamp=ts, message=msg)


def test_build_timeline_empty():
    tl = build_timeline([])
    assert len(tl) == 0
    assert tl.total_lines() == 0


def test_build_timeline_no_timestamps():
    lines = [make_line(None, n=i) for i in range(5)]
    tl = build_timeline(lines)
    assert len(tl) == 0


def test_build_timeline_single_bucket():
    lines = [make_line(dt(10, 0, i)) for i in range(5)]
    tl = build_timeline(lines, interval_seconds=60)
    assert len(tl) == 1
    assert tl.total_lines() == 5


def test_build_timeline_multiple_buckets():
    lines = [
        make_line(dt(10, 0, 0)),
        make_line(dt(10, 1, 0)),
        make_line(dt(10, 2, 0)),
    ]
    tl = build_timeline(lines, interval_seconds=60)
    assert len(tl) == 3
    assert tl.total_lines() == 3


def test_build_timeline_bucket_boundaries():
    lines = [
        make_line(dt(10, 0, 0)),
        make_line(dt(10, 0, 59)),
        make_line(dt(10, 1, 0)),
    ]
    tl = build_timeline(lines, interval_seconds=60)
    assert len(tl) == 2
    assert len(tl.buckets[0]) == 2
    assert len(tl.buckets[1]) == 1


def test_build_timeline_invalid_interval():
    with pytest.raises(ValueError):
        build_timeline([], interval_seconds=0)


def test_format_timeline_empty():
    tl = build_timeline([])
    out = format_timeline(tl)
    assert "no timestamped" in out


def test_format_timeline_renders_rows():
    lines = [make_line(dt(10, 0, i)) for i in range(3)]
    tl = build_timeline(lines, interval_seconds=60)
    out = format_timeline(tl)
    assert "10:00:00" in out
    assert "#" in out


def test_timeline_interval_stored():
    tl = build_timeline([], interval_seconds=30)
    assert tl.interval_seconds == 30


def test_bucket_len():
    b = TimelineBucket(start=dt(10, 0), end=dt(10, 1))
    b.lines = [make_line(dt(10, 0, i)) for i in range(7)]
    assert len(b) == 7

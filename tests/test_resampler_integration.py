"""Integration tests: resampler used alongside existing modules."""
from __future__ import annotations

from datetime import datetime, timezone

from logslice.parser import LogLine
from logslice.resampler import resample_lines, format_resampled
from logslice.filter import filter_lines


def make_line(msg: str, ts: datetime | None = None, level: str | None = None, n: int = 1) -> LogLine:
    return LogLine(raw=msg, line_number=n, timestamp=ts, level=level, message=msg)


def dt(h: int, m: int, s: int = 0) -> datetime:
    return datetime(2024, 6, 1, h, m, s, tzinfo=timezone.utc)


def _make_lines():
    return [
        make_line("INFO start",   dt(8, 0,  0),  level="INFO",    n=1),
        make_line("ERROR boom",   dt(8, 0, 30),  level="ERROR",   n=2),
        make_line("INFO ok",      dt(8, 1,  5),  level="INFO",    n=3),
        make_line("WARN slow",    dt(8, 1, 45),  level="WARNING", n=4),
        make_line("INFO done",    dt(8, 2,  0),  level="INFO",    n=5),
        make_line("no timestamp", None,          level=None,      n=6),
    ]


def test_resample_total_bucketed_plus_skipped_equals_input():
    lines = _make_lines()
    result = resample_lines(lines, interval_seconds=60)
    assert result.total_bucketed + result.skipped == len(lines)


def test_resample_then_format_line_count_matches_bucket_count():
    lines = _make_lines()
    result = resample_lines(lines, interval_seconds=60)
    rows = format_resampled(result)
    assert len(rows) == len(result)


def test_filter_then_resample_only_errors():
    lines = _make_lines()
    errors = filter_lines(lines, pattern="ERROR")
    result = resample_lines(errors, interval_seconds=60)
    assert result.total_bucketed == 1


def test_large_interval_collapses_all_into_one_bucket():
    lines = _make_lines()
    result = resample_lines(lines, interval_seconds=3600)
    assert len(result) == 1
    assert result.buckets[0].label.startswith("2024-06-01T08:00:00")


def test_small_interval_creates_many_buckets():
    lines = _make_lines()
    result = resample_lines(lines, interval_seconds=1)
    # each line with a distinct second gets its own bucket
    assert len(result) >= 4

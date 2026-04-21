# tests/test_trender_integration.py
from datetime import datetime, timezone
from logslice.parser import LogLine
from logslice.trender import build_trend, format_trend


def make_line(ts=None, msg="log", ln=1):
    return LogLine(raw=msg, message=msg, timestamp=ts, line_number=ln)


def dt(h, m=0, s=0):
    return datetime(2024, 6, 15, h, m, s, tzinfo=timezone.utc)


def test_mixed_with_and_without_timestamps():
    lines = [
        make_line(ts=dt(8, 0, 0)),
        make_line(ts=None),
        make_line(ts=dt(8, 0, 30)),
        make_line(ts=None),
    ]
    result = build_trend(lines, interval_seconds=60)
    assert result.total_lines == 2
    assert result.skipped == 2


def test_large_interval_collapses_all_into_one_bucket():
    lines = [make_line(ts=dt(h)) for h in range(6)]
    result = build_trend(lines, interval_seconds=86400)  # one day
    assert len(result) == 1
    assert result.points[0].count == 6


def test_trend_then_format_no_error():
    lines = [
        make_line(ts=dt(10, 0, 0)),
        make_line(ts=dt(10, 1, 0)),
        make_line(ts=dt(10, 1, 45)),
    ]
    result = build_trend(lines, interval_seconds=60)
    out = format_trend(result)
    assert isinstance(out, str)
    assert len(out) > 0


def test_peak_bucket_has_most_lines():
    lines = (
        [make_line(ts=dt(9, 0, 0)) for _ in range(10)]
        + [make_line(ts=dt(9, 1, 0)) for _ in range(3)]
        + [make_line(ts=dt(9, 2, 0)) for _ in range(6)]
    )
    result = build_trend(lines, interval_seconds=60)
    assert result.peak is not None
    assert result.peak.count == 10


def test_trough_bucket_has_fewest_lines():
    lines = (
        [make_line(ts=dt(9, 0, 0)) for _ in range(10)]
        + [make_line(ts=dt(9, 1, 0)) for _ in range(1)]
        + [make_line(ts=dt(9, 2, 0)) for _ in range(6)]
    )
    result = build_trend(lines, interval_seconds=60)
    assert result.trough is not None
    assert result.trough.count == 1

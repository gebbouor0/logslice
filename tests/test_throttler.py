import pytest
from datetime import datetime, timedelta
from logslice.parser import LogLine
from logslice.throttler import throttle_lines, ThrottleResult


def make_line(msg: str, ts=None, n: int = 1) -> LogLine:
    return LogLine(raw=msg, message=msg, timestamp=ts, line_number=n)


def dt(offset_seconds: int) -> datetime:
    return datetime(2024, 1, 1, 12, 0, 0) + timedelta(seconds=offset_seconds)


def test_throttle_basic_keeps_within_limit():
    lines = [make_line(f"msg{i}", dt(i), i) for i in range(5)]
    result = throttle_lines(lines, max_per_window=3, window_seconds=60)
    assert result.kept == 3
    assert result.dropped == 2


def test_throttle_new_window_resets_count():
    lines = [
        make_line("a", dt(0), 1),
        make_line("b", dt(1), 2),
        make_line("c", dt(2), 3),  # dropped
        make_line("d", dt(60), 4),  # new window
        make_line("e", dt(61), 5),
        make_line("f", dt(62), 6),  # dropped
    ]
    result = throttle_lines(lines, max_per_window=2, window_seconds=60)
    assert result.kept == 4
    assert result.dropped == 2


def test_throttle_no_timestamps_always_kept():
    lines = [make_line(f"msg{i}", None, i) for i in range(10)]
    result = throttle_lines(lines, max_per_window=2, window_seconds=60)
    assert result.kept == 10
    assert result.dropped == 0


def test_throttle_empty_input():
    result = throttle_lines([], max_per_window=5, window_seconds=60)
    assert result.kept == 0
    assert result.dropped == 0


def test_throttle_invalid_max_per_window():
    with pytest.raises(ValueError):
        throttle_lines([], max_per_window=0)


def test_throttle_invalid_window_seconds():
    with pytest.raises(ValueError):
        throttle_lines([], max_per_window=1, window_seconds=0)


def test_throttle_result_fields():
    lines = [make_line("x", dt(i), i) for i in range(3)]
    result = throttle_lines(lines, max_per_window=2, window_seconds=30)
    assert result.window_seconds == 30
    assert result.max_per_window == 2
    assert isinstance(result.lines, list)


def test_throttle_mixed_timestamps_and_none():
    lines = [
        make_line("a", dt(0), 1),
        make_line("b", dt(1), 2),
        make_line("c", dt(2), 3),  # dropped
        make_line("no-ts", None, 4),  # kept always
    ]
    result = throttle_lines(lines, max_per_window=2, window_seconds=60)
    assert result.kept == 3
    assert result.dropped == 1
    assert result.lines[2].message == "no-ts"

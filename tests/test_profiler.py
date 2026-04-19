import pytest
from datetime import datetime, timedelta
from logslice.parser import LogLine
from logslice.profiler import profile_lines, format_profile, ProfileResult


def make_line(message: str, ts=None, n: int = 1) -> LogLine:
    return LogLine(raw=message, message=message, timestamp=ts, line_number=n)


def dt(hour: int, minute: int = 0, second: int = 0) -> datetime:
    return datetime(2024, 1, 1, hour, minute, second)


def test_profile_empty():
    result = profile_lines([])
    assert result.total_lines == 0
    assert result.avg_message_length == 0.0
    assert result.duration is None
    assert result.lines_per_second is None


def test_profile_total_lines():
    lines = [make_line("hello", n=i) for i in range(5)]
    result = profile_lines(lines)
    assert result.total_lines == 5


def test_profile_avg_message_length():
    lines = [make_line("ab"), make_line("abcd"), make_line("abcdef")]
    result = profile_lines(lines)
    assert result.avg_message_length == pytest.approx((2 + 4 + 6) / 3)


def test_profile_min_max_length():
    lines = [make_line("a"), make_line("abc"), make_line("abcde")]
    result = profile_lines(lines)
    assert result.min_message_length == 1
    assert result.max_message_length == 5


def test_profile_timestamp_coverage():
    lines = [
        make_line("a", ts=dt(10)),
        make_line("b", ts=dt(11)),
        make_line("c"),
        make_line("d"),
    ]
    result = profile_lines(lines)
    assert result.lines_with_timestamp == 2
    assert result.timestamp_coverage == pytest.approx(0.5)


def test_profile_duration():
    lines = [
        make_line("a", ts=dt(10, 0, 0)),
        make_line("b", ts=dt(10, 0, 30)),
        make_line("c", ts=dt(10, 1, 0)),
    ]
    result = profile_lines(lines)
    assert result.duration == timedelta(minutes=1)


def test_profile_lines_per_second():
    lines = [
        make_line("a", ts=dt(10, 0, 0)),
        make_line("b", ts=dt(10, 0, 10)),
    ]
    result = profile_lines(lines)
    assert result.lines_per_second == pytest.approx(2 / 10)


def test_profile_empty_messages():
    lines = [make_line(""), make_line("  "), make_line("hello")]
    result = profile_lines(lines)
    assert result.empty_messages == 2


def test_format_profile_contains_fields():
    lines = [make_line("hello", ts=dt(9)), make_line("world", ts=dt(10))]
    result = profile_lines(lines)
    output = format_profile(result)
    assert "Total lines" in output
    assert "Duration" in output
    assert "Lines/second" in output
    assert "Empty messages" in output


def test_profile_no_timestamps_duration_none():
    lines = [make_line("x"), make_line("y")]
    result = profile_lines(lines)
    assert result.duration is None
    assert result.lines_per_second is None

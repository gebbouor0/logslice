"""Tests for logslice.streaker."""
import pytest
from datetime import datetime, timezone
from logslice.parser import LogLine
from logslice.streaker import detect_streaks, format_streaks, Streak, StreakResult


def make_line(n: int, message: str, ts: datetime = None) -> LogLine:
    return LogLine(raw=message, line_number=n, timestamp=ts, message=message)


def dt(second: int) -> datetime:
    return datetime(2024, 1, 1, 12, 0, second, tzinfo=timezone.utc)


def is_error(line: LogLine) -> bool:
    return "ERROR" in line.message


def test_detect_no_streaks():
    lines = [make_line(i, "INFO ok") for i in range(5)]
    result = detect_streaks(lines, is_error)
    assert len(result) == 0
    assert result.total_matched == 0
    assert result.total_input == 5


def test_detect_single_streak():
    lines = [
        make_line(1, "INFO start"),
        make_line(2, "ERROR a"),
        make_line(3, "ERROR b"),
        make_line(4, "INFO end"),
    ]
    result = detect_streaks(lines, is_error)
    assert len(result) == 1
    assert len(result.streaks[0]) == 2


def test_detect_multiple_streaks():
    lines = [
        make_line(1, "ERROR x"),
        make_line(2, "INFO ok"),
        make_line(3, "ERROR y"),
        make_line(4, "ERROR z"),
    ]
    result = detect_streaks(lines, is_error)
    assert len(result) == 2
    assert len(result.streaks[0]) == 1
    assert len(result.streaks[1]) == 2


def test_min_length_filters_short_streaks():
    lines = [
        make_line(1, "ERROR x"),
        make_line(2, "INFO ok"),
        make_line(3, "ERROR y"),
        make_line(4, "ERROR z"),
        make_line(5, "ERROR w"),
    ]
    result = detect_streaks(lines, is_error, min_length=2)
    assert len(result) == 1
    assert len(result.streaks[0]) == 3


def test_streak_timestamps():
    lines = [
        make_line(1, "ERROR a", dt(0)),
        make_line(2, "ERROR b", dt(5)),
        make_line(3, "ERROR c", dt(10)),
    ]
    result = detect_streaks(lines, is_error)
    streak = result.streaks[0]
    assert streak.start_time == dt(0)
    assert streak.end_time == dt(10)
    assert streak.duration_seconds == 10.0


def test_streak_no_timestamps():
    lines = [make_line(i, "ERROR x") for i in range(3)]
    result = detect_streaks(lines, is_error)
    streak = result.streaks[0]
    assert streak.duration_seconds is None


def test_longest_streak():
    lines = [
        make_line(1, "ERROR a"),
        make_line(2, "INFO ok"),
        make_line(3, "ERROR b"),
        make_line(4, "ERROR c"),
        make_line(5, "ERROR d"),
    ]
    result = detect_streaks(lines, is_error)
    assert len(result.longest) == 3


def test_longest_streak_empty():
    result = StreakResult()
    assert result.longest is None


def test_invalid_min_length():
    with pytest.raises(ValueError):
        detect_streaks([], is_error, min_length=0)


def test_total_matched():
    lines = [
        make_line(1, "ERROR a"),
        make_line(2, "INFO ok"),
        make_line(3, "ERROR b"),
    ]
    result = detect_streaks(lines, is_error)
    assert result.total_matched == 2


def test_format_streaks_output():
    lines = [
        make_line(1, "ERROR a"),
        make_line(2, "ERROR b"),
    ]
    result = detect_streaks(lines, is_error)
    out = format_streaks(result)
    assert any("Streak 1" in l for l in out)
    assert any("ERROR a" in l for l in out)

"""Integration tests for streaker: end-to-end streak detection scenarios."""
from datetime import datetime, timezone
from logslice.parser import LogLine
from logslice.streaker import detect_streaks, format_streaks


def make_line(n: int, message: str, ts: datetime = None) -> LogLine:
    return LogLine(raw=message, line_number=n, timestamp=ts, message=message)


def dt(second: int) -> datetime:
    return datetime(2024, 1, 1, 0, 0, second, tzinfo=timezone.utc)


def test_all_lines_match_is_one_streak():
    lines = [make_line(i, "ERROR x") for i in range(10)]
    result = detect_streaks(lines, lambda l: "ERROR" in l.message)
    assert len(result) == 1
    assert len(result.streaks[0]) == 10


def test_streak_at_end_of_input():
    lines = [
        make_line(1, "INFO ok"),
        make_line(2, "ERROR a"),
        make_line(3, "ERROR b"),
    ]
    result = detect_streaks(lines, lambda l: "ERROR" in l.message)
    assert len(result) == 1
    assert len(result.streaks[0]) == 2


def test_streak_at_start_of_input():
    lines = [
        make_line(1, "ERROR a"),
        make_line(2, "ERROR b"),
        make_line(3, "INFO ok"),
    ]
    result = detect_streaks(lines, lambda l: "ERROR" in l.message)
    assert len(result) == 1
    assert len(result.streaks[0]) == 2


def test_format_streaks_no_streaks():
    result = detect_streaks([], lambda l: True)
    out = format_streaks(result)
    assert len(out) >= 1
    assert "0" in out[0]


def test_total_input_and_matched_consistent():
    lines = [make_line(i, "ERROR" if i % 2 == 0 else "INFO ok") for i in range(20)]
    result = detect_streaks(lines, lambda l: "ERROR" in l.message)
    assert result.total_input == 20
    assert result.total_matched == 10

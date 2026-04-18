import pytest
from datetime import datetime
from logslice.parser import LogLine
from logslice.counter import (
    count_by_pattern,
    count_by_field,
    count_by_hour,
    format_count_result,
    CountResult,
)


def make_line(msg: str, level: str = "INFO", ts: datetime = None, n: int = 1) -> LogLine:
    return LogLine(line_number=n, raw=msg, message=msg, level=level, timestamp=ts)


def test_count_by_pattern_basic():
    lines = [make_line("error occurred"), make_line("all good"), make_line("another error")]
    assert count_by_pattern(lines, r"error") == 2


def test_count_by_pattern_no_match():
    lines = [make_line("hello"), make_line("world")]
    assert count_by_pattern(lines, r"error") == 0


def test_count_by_pattern_empty():
    assert count_by_pattern([], r"error") == 0


def test_count_by_field_level():
    lines = [
        make_line("a", level="INFO"),
        make_line("b", level="ERROR"),
        make_line("c", level="INFO"),
    ]
    result = count_by_field(lines, "level")
    assert result.total == 3
    assert result.by_field["INFO"] == 2
    assert result.by_field["ERROR"] == 1
    assert result.field_name == "level"


def test_count_by_field_none_value():
    lines = [make_line("a", level=None)]
    result = count_by_field(lines, "level")
    assert "None" in result.by_field or "<none>" in result.by_field


def test_count_by_hour_groups_correctly():
    ts1 = datetime(2024, 1, 1, 10, 15)
    ts2 = datetime(2024, 1, 1, 10, 45)
    ts3 = datetime(2024, 1, 1, 11, 5)
    lines = [make_line("a", ts=ts1), make_line("b", ts=ts2), make_line("c", ts=ts3)]
    result = count_by_hour(lines)
    assert result.by_field["2024-01-01 10:00"] == 2
    assert result.by_field["2024-01-01 11:00"] == 1


def test_count_by_hour_no_timestamp():
    lines = [make_line("x", ts=None)]
    result = count_by_hour(lines)
    assert result.by_field.get("<no timestamp>") == 1


def test_top_returns_sorted():
    r = CountResult(total=3, by_field={"a": 1, "b": 2, "c": 3}, field_name="x")
    top = r.top(2)
    assert top[0] == ("c", 3)
    assert top[1] == ("b", 2)


def test_least_returns_sorted():
    r = CountResult(total=3, by_field={"a": 1, "b": 2, "c": 3}, field_name="x")
    least = r.least(2)
    assert least[0] == ("a", 1)


def test_format_count_result_contains_total():
    r = CountResult(total=5, by_field={"INFO": 3, "ERROR": 2}, field_name="level")
    out = format_count_result(r)
    assert "Total lines: 5" in out
    assert "INFO" in out
    assert "ERROR" in out


def test_format_count_result_top_n():
    r = CountResult(total=3, by_field={"a": 1, "b": 2, "c": 3}, field_name="x")
    out = format_count_result(r, top_n=2)
    assert "c" in out
    assert "b" in out

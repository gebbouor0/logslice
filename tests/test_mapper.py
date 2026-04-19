import pytest
from datetime import datetime
from logslice.parser import LogLine
from logslice.mapper import map_lines, map_field, format_mapped, MapResult


def make_line(msg: str, line_number: int = 1, ts: datetime = None) -> LogLine:
    return LogLine(raw=msg, message=msg, timestamp=ts, line_number=line_number)


def test_map_lines_basic():
    lines = [make_line("hello", 1), make_line("world", 2)]
    result = map_lines(lines, lambda l: l.message.upper())
    assert len(result) == 2
    assert result.values() == ["HELLO", "WORLD"]


def test_map_lines_empty():
    result = map_lines([], lambda l: l.message)
    assert len(result) == 0
    assert result.values() == []


def test_map_lines_preserves_original():
    line = make_line("test", 5)
    result = map_lines([line], lambda l: 42)
    assert result.lines[0].original is line
    assert result.lines[0].line_number == 5
    assert result.lines[0].raw == "test"


def test_map_field_message():
    lines = [make_line("alpha", 1), make_line("beta", 2)]
    result = map_field(lines, "message")
    assert result.values() == ["alpha", "beta"]


def test_map_field_line_number():
    lines = [make_line("a", 10), make_line("b", 20)]
    result = map_field(lines, "line_number")
    assert result.values() == [10, 20]


def test_map_field_missing_attr():
    lines = [make_line("x", 1)]
    result = map_field(lines, "nonexistent_field")
    assert result.values() == [None]


def test_map_field_timestamp():
    ts = datetime(2024, 1, 1, 12, 0, 0)
    lines = [make_line("msg", 1, ts=ts)]
    result = map_field(lines, "timestamp")
    assert result.values() == [ts]


def test_format_mapped_default_sep():
    lines = [make_line("hello", 1)]
    result = map_lines(lines, lambda l: "HELLO")
    formatted = format_mapped(result)
    assert formatted == ["hello => HELLO"]


def test_format_mapped_custom_sep():
    lines = [make_line("foo", 1), make_line("bar", 2)]
    result = map_lines(lines, lambda l: len(l.message))
    formatted = format_mapped(result, sep=" -> ")
    assert formatted == ["foo -> 3", "bar -> 3"]


def test_format_mapped_empty():
    result = MapResult()
    assert format_mapped(result) == []

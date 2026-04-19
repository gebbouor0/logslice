import pytest
from logslice.parser import LogLine
from logslice.offsetter import offset_lines, format_offset, OffsetLine


def make_line(n: int, msg: str = "hello") -> LogLine:
    return LogLine(raw=f"{msg} {n}", timestamp=None, message=f"{msg} {n}", line_number=n)


def test_offset_positive():
    lines = [make_line(1), make_line(2), make_line(3)]
    result = offset_lines(lines, 100)
    assert result.lines[0].line_number == 101
    assert result.lines[2].line_number == 103


def test_offset_zero():
    lines = [make_line(5)]
    result = offset_lines(lines, 0)
    assert result.lines[0].line_number == 5


def test_offset_negative():
    lines = [make_line(10), make_line(11)]
    result = offset_lines(lines, -5)
    assert result.lines[0].line_number == 5
    assert result.lines[1].line_number == 6


def test_offset_preserves_raw():
    line = make_line(3, msg="ERROR")
    result = offset_lines([line], 10)
    assert result.lines[0].raw == "ERROR 3"


def test_offset_preserves_message():
    line = make_line(7)
    result = offset_lines([line], 1)
    assert result.lines[0].message == line.message


def test_offset_len():
    lines = [make_line(i) for i in range(1, 6)]
    result = offset_lines(lines, 50)
    assert len(result) == 5


def test_offset_empty():
    result = offset_lines([], 10)
    assert len(result) == 0


def test_offset_result_stores_offset():
    result = offset_lines([make_line(1)], 42)
    assert result.offset == 42


def test_format_offset_contains_line_number():
    lines = [make_line(1)]
    result = offset_lines(lines, 9)
    output = format_offset(result)
    assert "10" in output
    assert "hello 1" in output


def test_format_offset_multiple_lines():
    lines = [make_line(i) for i in range(1, 4)]
    result = offset_lines(lines, 0)
    output = format_offset(result)
    assert output.count("\n") == 2

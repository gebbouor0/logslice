"""Tests for logslice/marker.py"""
import pytest
from logslice.parser import LogLine
from logslice.marker import mark_lines, format_marked, MarkedLine, MarkResult


def make_line(msg: str, n: int = 1) -> LogLine:
    return LogLine(raw=msg, message=msg, line_number=n, timestamp=None, level=None)


def always_false(_: LogLine) -> bool:
    return False


def is_error(line: LogLine) -> bool:
    return "ERROR" in line.message


def test_mark_predicate_match():
    lines = [make_line("ERROR something", 1), make_line("INFO ok", 2)]
    result = mark_lines(lines, predicate=is_error)
    assert result.lines[0].marker == "*"
    assert result.lines[1].marker is None


def test_mark_predicate_no_match():
    lines = [make_line("INFO all good", 1)]
    result = mark_lines(lines, predicate=is_error)
    assert result.lines[0].marker is None


def test_mark_first():
    lines = [make_line("a", 1), make_line("b", 2), make_line("c", 3)]
    result = mark_lines(lines, predicate=always_false, mark_first=True)
    assert result.lines[0].marker == "first"
    assert result.lines[1].marker is None


def test_mark_last():
    lines = [make_line("a", 1), make_line("b", 2), make_line("c", 3)]
    result = mark_lines(lines, predicate=always_false, mark_last=True)
    assert result.lines[2].marker == "last"
    assert result.lines[0].marker is None


def test_mark_every_nth():
    lines = [make_line(str(i), i) for i in range(6)]
    result = mark_lines(lines, predicate=always_false, every_nth=2)
    markers = [l.marker for l in result.lines]
    assert markers[0] == "nth(2)"
    assert markers[2] == "nth(2)"
    assert markers[4] == "nth(2)"
    assert markers[1] is None


def test_mark_custom_marker_label():
    lines = [make_line("WARN hi", 1)]
    result = mark_lines(lines, predicate=lambda l: "WARN" in l.message, marker="!")
    assert result.lines[0].marker == "!"


def test_mark_result_len():
    lines = [make_line("a", i) for i in range(5)]
    result = mark_lines(lines, predicate=always_false)
    assert len(result) == 5


def test_mark_result_marked_and_unmarked():
    lines = [make_line("ERROR x", 1), make_line("INFO y", 2), make_line("ERROR z", 3)]
    result = mark_lines(lines, predicate=is_error)
    assert len(result.marked()) == 2
    assert len(result.unmarked()) == 1


def test_mark_empty_input():
    result = mark_lines([], predicate=is_error)
    assert len(result) == 0
    assert result.marked() == []


def test_format_marked_output():
    lines = [make_line("ERROR boom", 1), make_line("INFO ok", 2)]
    result = mark_lines(lines, predicate=is_error)
    out = format_marked(result)
    assert len(out) == 2
    assert "[*]" in out[0]
    assert "ERROR boom" in out[0]
    assert "[*]" not in out[1]


def test_format_marked_empty():
    result = mark_lines([], predicate=always_false)
    assert format_marked(result) == []

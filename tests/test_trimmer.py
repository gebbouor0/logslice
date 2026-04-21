"""Tests for logslice.trimmer."""
import pytest
from logslice.parser import LogLine
from logslice.trimmer import trim_head, trim_tail, trim_lines, TrimResult


def make_line(n: int, msg: str = "hello") -> LogLine:
    return LogLine(raw=f"line {n}", line_number=n, timestamp=None, message=msg)


def make_lines(n: int) -> list:
    return [make_line(i) for i in range(1, n + 1)]


# --- trim_head ---

def test_trim_head_basic():
    lines = make_lines(5)
    result = trim_head(lines, count=2)
    assert len(result) == 3
    assert result.trimmed_head == 2
    assert result.trimmed_tail == 0
    assert result.lines[0].line_number == 3


def test_trim_head_more_than_available():
    lines = make_lines(3)
    result = trim_head(lines, count=10)
    assert len(result) == 0
    assert result.trimmed_head == 3


def test_trim_head_zero_removes_nothing():
    lines = make_lines(4)
    result = trim_head(lines, count=0)
    assert len(result) == 4
    assert result.trimmed_head == 0


def test_trim_head_predicate():
    lines = make_lines(5)
    result = trim_head(lines, predicate=lambda l: l.line_number <= 3)
    assert result.trimmed_head == 3
    assert result.lines[0].line_number == 4


def test_trim_head_predicate_no_match():
    lines = make_lines(3)
    result = trim_head(lines, predicate=lambda l: False)
    assert result.trimmed_head == 0
    assert len(result) == 3


def test_trim_head_negative_raises():
    with pytest.raises(ValueError):
        trim_head(make_lines(3), count=-1)


# --- trim_tail ---

def test_trim_tail_basic():
    lines = make_lines(5)
    result = trim_tail(lines, count=2)
    assert len(result) == 3
    assert result.trimmed_tail == 2
    assert result.trimmed_head == 0
    assert result.lines[-1].line_number == 3


def test_trim_tail_more_than_available():
    lines = make_lines(3)
    result = trim_tail(lines, count=10)
    assert len(result) == 0
    assert result.trimmed_tail == 3


def test_trim_tail_predicate():
    lines = make_lines(5)
    result = trim_tail(lines, predicate=lambda l: l.line_number >= 4)
    assert result.trimmed_tail == 2
    assert result.lines[-1].line_number == 3


def test_trim_tail_negative_raises():
    with pytest.raises(ValueError):
        trim_tail(make_lines(3), count=-1)


# --- trim_lines ---

def test_trim_lines_both_ends():
    lines = make_lines(10)
    result = trim_lines(lines, head=2, tail=3)
    assert result.trimmed_head == 2
    assert result.trimmed_tail == 3
    assert len(result) == 5
    assert result.total_trimmed == 5


def test_trim_lines_empty_input():
    result = trim_lines([], head=2, tail=2)
    assert len(result) == 0
    assert result.total_trimmed == 0


def test_trim_lines_predicate_both_ends():
    lines = [
        make_line(1, "DEBUG start"),
        make_line(2, "INFO body"),
        make_line(3, "INFO body2"),
        make_line(4, "DEBUG end"),
    ]
    result = trim_lines(lines, predicate=lambda l: "DEBUG" in l.message)
    assert result.trimmed_head == 1
    assert result.trimmed_tail == 1
    assert len(result) == 2

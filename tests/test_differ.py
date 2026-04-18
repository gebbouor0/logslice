"""Tests for logslice.differ."""
import pytest
from datetime import datetime
from logslice.parser import LogLine
from logslice.differ import diff_streams, format_diff, diff_and_format, DiffLine


def make_line(raw: str, line_number: int = 1) -> LogLine:
    return LogLine(raw=raw, timestamp=None, level=None, message=raw.strip(), line_number=line_number)


LEFT = [make_line("alpha", 1), make_line("beta", 2), make_line("gamma", 3)]
RIGHT = [make_line("beta", 1), make_line("gamma", 2), make_line("delta", 3)]


def test_diff_removed():
    result = diff_streams(LEFT, RIGHT)
    removed = [d for d in result if d.status == "removed"]
    assert len(removed) == 1
    assert removed[0].raw.strip() == "alpha"


def test_diff_added():
    result = diff_streams(LEFT, RIGHT)
    added = [d for d in result if d.status == "added"]
    assert len(added) == 1
    assert added[0].raw.strip() == "delta"


def test_diff_common():
    result = diff_streams(LEFT, RIGHT)
    common = [d for d in result if d.status == "common"]
    assert len(common) == 2


def test_diff_empty_streams():
    result = diff_streams([], [])
    assert result == []


def test_diff_all_added():
    result = diff_streams([], RIGHT)
    assert all(d.status == "added" for d in result)
    assert len(result) == len(RIGHT)


def test_diff_all_removed():
    result = diff_streams(LEFT, [])
    assert all(d.status == "removed" for d in result)


def test_format_diff_prefixes():
    result = diff_streams(LEFT, RIGHT)
    lines = format_diff(result)
    for line in lines:
        assert line.startswith(("+ ", "- ", "  "))


def test_format_diff_color_added():
    diff = [DiffLine(line=make_line("new entry"), status="added")]
    lines = format_diff(diff, color=True)
    assert "\033[32m" in lines[0]
    assert "\033[0m" in lines[0]


def test_format_diff_color_removed():
    diff = [DiffLine(line=make_line("old entry"), status="removed")]
    lines = format_diff(diff, color=True)
    assert "\033[31m" in lines[0]


def test_format_diff_no_color_common():
    diff = [DiffLine(line=make_line("same"), status="common")]
    lines = format_diff(diff, color=True)
    assert "\033[" not in lines[0]


def test_diff_and_format_returns_strings():
    lines = diff_and_format(LEFT, RIGHT)
    assert all(isinstance(l, str) for l in lines)


def test_diff_line_raw_and_number():
    dl = DiffLine(line=make_line("hello", 7), status="common")
    assert dl.raw == "hello"
    assert dl.line_number == 7

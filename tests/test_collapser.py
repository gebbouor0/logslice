"""Tests for logslice/collapser.py"""
import pytest
from logslice.parser import LogLine
from logslice.collapser import (
    collapse_lines,
    format_collapsed,
    CollapsedLine,
    CollapseResult,
)


def make_line(msg: str, n: int = 1) -> LogLine:
    return LogLine(raw=msg, message=msg, line_number=n, timestamp=None, level=None)


def test_collapse_empty_input():
    result = collapse_lines([])
    assert len(result) == 0
    assert result.total_input == 0
    assert result.total_output == 0
    assert result.collapsed_count == 0


def test_collapse_no_duplicates():
    lines = [make_line("alpha"), make_line("beta"), make_line("gamma")]
    result = collapse_lines(lines)
    assert len(result) == 3
    assert result.total_input == 3
    assert result.total_output == 3
    assert result.collapsed_count == 0
    assert all(item.repeat_count == 1 for item in result.items)


def test_collapse_consecutive_duplicates():
    lines = [make_line("same"), make_line("same"), make_line("same")]
    result = collapse_lines(lines)
    assert len(result) == 1
    assert result.items[0].repeat_count == 3
    assert result.collapsed_count == 2


def test_collapse_non_consecutive_not_merged():
    lines = [make_line("a"), make_line("b"), make_line("a")]
    result = collapse_lines(lines)
    assert len(result) == 3
    assert all(item.repeat_count == 1 for item in result.items)


def test_collapse_mixed_runs():
    lines = [
        make_line("err"), make_line("err"),
        make_line("ok"),
        make_line("err"), make_line("err"), make_line("err"),
    ]
    result = collapse_lines(lines)
    assert len(result) == 3
    assert result.items[0].repeat_count == 2
    assert result.items[1].repeat_count == 1
    assert result.items[2].repeat_count == 3
    assert result.collapsed_count == 3


def test_collapse_single_line():
    lines = [make_line("only one")]
    result = collapse_lines(lines)
    assert len(result) == 1
    assert result.items[0].repeat_count == 1


def test_collapse_custom_key():
    lines = [make_line("ERROR: 1"), make_line("ERROR: 2"), make_line("INFO: 1")]
    # key on first word only
    result = collapse_lines(lines, key=lambda l: l.message.split(":")[0])
    assert len(result) == 2
    assert result.items[0].repeat_count == 2
    assert result.items[1].repeat_count == 1


def test_format_collapsed_no_repeats():
    lines = [make_line("alpha"), make_line("beta")]
    result = collapse_lines(lines)
    formatted = format_collapsed(result)
    assert formatted == ["alpha", "beta"]


def test_format_collapsed_with_repeats():
    lines = [make_line("boom"), make_line("boom"), make_line("boom")]
    result = collapse_lines(lines)
    formatted = format_collapsed(result)
    assert len(formatted) == 1
    assert "(x3)" in formatted[0]


def test_format_collapsed_mixed():
    lines = [make_line("a"), make_line("a"), make_line("b")]
    result = collapse_lines(lines)
    formatted = format_collapsed(result)
    assert "(x2)" in formatted[0]
    assert "(x" not in formatted[1]

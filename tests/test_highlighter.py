"""Tests for logslice.highlighter module."""

import pytest
from logslice.highlighter import colorize, highlight_pattern, highlight_lines, ANSI_COLORS
from logslice.parser import LogLine


def make_log_line(raw: str, line_number: int = 1) -> LogLine:
    return LogLine(raw=raw, timestamp=None, level=None, message=raw, line_number=line_number)


def test_colorize_wraps_text():
    result = colorize("hello", "red")
    assert ANSI_COLORS["red"] in result
    assert "hello" in result
    assert ANSI_COLORS["reset"] in result


def test_colorize_unknown_color_uses_default():
    result = colorize("hello", "notacolor")
    assert ANSI_COLORS["yellow"] in result
    assert "hello" in result


def test_highlight_pattern_basic():
    line = "ERROR something went wrong"
    result = highlight_pattern(line, "ERROR", "red")
    assert ANSI_COLORS["red"] in result
    assert "ERROR" in result
    assert "something went wrong" in result


def test_highlight_pattern_no_match_returns_original():
    line = "INFO all good"
    result = highlight_pattern(line, "ERROR")
    assert result == line


def test_highlight_pattern_empty_pattern_returns_original():
    line = "INFO all good"
    result = highlight_pattern(line, "")
    assert result == line


def test_highlight_pattern_invalid_regex_falls_back_to_literal():
    line = "price is $100"
    # '$100' is invalid regex but valid literal
    result = highlight_pattern(line, "$100", "cyan")
    assert ANSI_COLORS["cyan"] in result
    assert "$100" in result


def test_highlight_lines_applies_color():
    lines = [
        make_log_line("ERROR disk full", 1),
        make_log_line("INFO started", 2),
    ]
    results = highlight_lines(lines, pattern="ERROR", color="red", use_color=True)
    assert len(results) == 2
    assert ANSI_COLORS["red"] in results[0]
    assert ANSI_COLORS["red"] not in results[1]


def test_highlight_lines_no_color_returns_raw():
    lines = [make_log_line("ERROR disk full", 1)]
    results = highlight_lines(lines, pattern="ERROR", use_color=False)
    assert results[0] == "ERROR disk full"


def test_highlight_lines_no_pattern():
    lines = [make_log_line("ERROR disk full", 1)]
    results = highlight_lines(lines, pattern=None, use_color=True)
    assert results[0] == "ERROR disk full"

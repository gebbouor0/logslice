"""Tests for logslice/squasher.py"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

import pytest

from logslice.parser import LogLine
from logslice.squasher import SquashedLine, squash_lines, format_squashed


def make_line(message: str, line_number: int = 1, ts: Optional[datetime] = None) -> LogLine:
    return LogLine(
        raw=message + "\n",
        line_number=line_number,
        timestamp=ts,
        level=None,
        message=message,
    )


def test_squash_empty_input():
    result = squash_lines([])
    assert len(result) == 0
    assert result.total_input == 0
    assert result.total_squashed == 0


def test_squash_no_duplicates():
    lines = [make_line("alpha", 1), make_line("beta", 2), make_line("gamma", 3)]
    result = squash_lines(lines)
    assert len(result) == 3
    assert result.total_squashed == 0
    assert all(sl.repeat_count == 1 for sl in result.lines)


def test_squash_consecutive_duplicates():
    lines = [make_line("error", i) for i in range(1, 5)]
    result = squash_lines(lines)
    assert len(result) == 1
    assert result.lines[0].repeat_count == 4
    assert result.total_squashed == 3


def test_squash_non_consecutive_not_merged():
    lines = [
        make_line("error", 1),
        make_line("info", 2),
        make_line("error", 3),
    ]
    result = squash_lines(lines)
    assert len(result) == 3
    assert result.total_squashed == 0


def test_squash_case_insensitive_default():
    lines = [make_line("Error", 1), make_line("error", 2), make_line("ERROR", 3)]
    result = squash_lines(lines)
    assert len(result) == 1
    assert result.lines[0].repeat_count == 3


def test_squash_case_sensitive_flag():
    lines = [make_line("Error", 1), make_line("error", 2)]
    result = squash_lines(lines, case_sensitive=True)
    assert len(result) == 2
    assert all(sl.repeat_count == 1 for sl in result.lines)


def test_squash_preserves_first_line_of_run():
    lines = [make_line("repeated", 1), make_line("repeated", 2)]
    result = squash_lines(lines)
    assert result.lines[0].line_number == 1


def test_format_squashed_no_repeat():
    lines = [make_line("hello", 1)]
    result = squash_lines(lines)
    formatted = format_squashed(result)
    assert formatted == ["hello"]


def test_format_squashed_with_repeat():
    lines = [make_line("boom", i) for i in range(1, 4)]
    result = squash_lines(lines)
    formatted = format_squashed(result)
    assert len(formatted) == 1
    assert "[x3]" in formatted[0]


def test_squash_total_input_tracked():
    lines = [make_line("x", i) for i in range(1, 8)]
    result = squash_lines(lines)
    assert result.total_input == 7

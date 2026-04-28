"""Tests for logslice/inverter.py"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

import pytest

from logslice.parser import LogLine
from logslice.inverter import invert_lines, format_inverted, InvertResult


def make_line(
    message: str,
    line_number: int = 1,
    timestamp: Optional[datetime] = None,
) -> LogLine:
    return LogLine(
        raw=message,
        line_number=line_number,
        timestamp=timestamp,
        message=message,
    )


def test_invert_no_patterns_keeps_all():
    lines = [make_line("hello", 1), make_line("world", 2)]
    result = invert_lines(lines, patterns=[])
    assert len(result.kept) == 2
    assert len(result.dropped) == 0


def test_invert_drops_matching_lines():
    lines = [
        make_line("ERROR something bad", 1),
        make_line("INFO all good", 2),
        make_line("ERROR another error", 3),
    ]
    result = invert_lines(lines, patterns=["ERROR"])
    assert len(result.kept) == 1
    assert result.kept[0].message == "INFO all good"
    assert len(result.dropped) == 2


def test_invert_case_insensitive_default():
    lines = [make_line("error lowercase", 1), make_line("INFO ok", 2)]
    result = invert_lines(lines, patterns=["error"])
    assert len(result.kept) == 1
    assert result.kept[0].message == "INFO ok"


def test_invert_case_sensitive_flag():
    lines = [make_line("error lowercase", 1), make_line("ERROR uppercase", 2)]
    result = invert_lines(lines, patterns=["error"], case_sensitive=True)
    # only "error lowercase" is dropped; "ERROR uppercase" is kept
    assert len(result.kept) == 1
    assert result.kept[0].message == "ERROR uppercase"


def test_invert_multiple_patterns():
    lines = [
        make_line("DEBUG verbose", 1),
        make_line("INFO normal", 2),
        make_line("WARN careful", 3),
        make_line("ERROR bad", 4),
    ]
    result = invert_lines(lines, patterns=["DEBUG", "ERROR"])
    messages = [l.message for l in result.kept]
    assert "INFO normal" in messages
    assert "WARN careful" in messages
    assert "DEBUG verbose" not in messages
    assert "ERROR bad" not in messages


def test_invert_empty_input():
    result = invert_lines([], patterns=["ERROR"])
    assert len(result) == 0
    assert result.total_input == 0


def test_invert_drop_rate():
    lines = [make_line("ERROR a", i) for i in range(3)] + \
            [make_line("INFO b", i + 3) for i in range(7)]
    result = invert_lines(lines, patterns=["ERROR"])
    assert result.drop_rate == pytest.approx(0.3)


def test_invert_drop_rate_empty_input():
    """drop_rate should be 0.0 when there are no input lines to avoid division by zero."""
    result = invert_lines([], patterns=["ERROR"])
    assert result.drop_rate == 0.0


def test_invert_total_input():
    lines = [make_line(f"line {i}", i) for i in range(5)]
    result = invert_lines(lines, patterns=["line 2"])
    assert result.total_input == 5


def test_format_inverted_basic():
    dt = datetime(2024, 1, 1, 12, 0, 0)
    lines = [make_line("INFO hello", 1, timestamp=dt)]
    result = invert_lines(lines, patterns=["ERROR"])
    formatted = format_inverted(result)
    assert len(formatted) == 1


def test_format_inverted_empty():
    """format_inverted on an empty result should return an empty list."""
    result = invert_lines([], patterns=["ERROR"])
    formatted = format_inverted(result)
    assert formatted == []

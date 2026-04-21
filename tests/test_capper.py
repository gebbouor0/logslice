"""Tests for logslice/capper.py."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

import pytest

from logslice.parser import LogLine
from logslice.capper import (
    cap_message,
    cap_lines,
    format_capped,
    CappedLine,
    CapResult,
)


def make_line(message: str, ts: Optional[datetime] = None, n: int = 1) -> LogLine:
    return LogLine(raw=message, timestamp=ts, message=message, line_number=n)


# --- cap_message ---

def test_cap_message_no_truncation():
    msg, capped = cap_message("hello", max_length=10)
    assert msg == "hello"
    assert capped is False


def test_cap_message_exact_length():
    msg, capped = cap_message("hello", max_length=5)
    assert msg == "hello"
    assert capped is False


def test_cap_message_truncates():
    msg, capped = cap_message("hello world", max_length=8)
    assert capped is True
    assert len(msg) == 8
    assert msg.endswith("...")


def test_cap_message_custom_ellipsis():
    msg, capped = cap_message("abcdefgh", max_length=5, ellipsis="!")
    assert capped is True
    assert msg == "abcd!"
    assert len(msg) == 5


def test_cap_message_max_length_zero():
    msg, capped = cap_message("anything", max_length=0)
    assert capped is True
    assert msg == ""


def test_cap_message_invalid_max_length():
    with pytest.raises(ValueError):
        cap_message("x", max_length=-1)


# --- cap_lines ---

def test_cap_lines_no_capping():
    lines = [make_line("short", n=i) for i in range(3)]
    result = cap_lines(lines, max_length=100)
    assert result.total_input == 3
    assert result.total_capped == 0
    assert all(not item.capped for item in result.items)


def test_cap_lines_all_capped():
    lines = [make_line("a very long message here", n=i) for i in range(4)]
    result = cap_lines(lines, max_length=10)
    assert result.total_capped == 4
    assert all(item.capped for item in result.items)


def test_cap_lines_preserves_original_message():
    original = "this is a long message"
    lines = [make_line(original, n=1)]
    result = cap_lines(lines, max_length=10)
    assert result.items[0].original_message == original


def test_cap_lines_capped_message_length():
    lines = [make_line("0123456789extra", n=1)]
    result = cap_lines(lines, max_length=10)
    assert len(result.items[0].message) == 10


def test_cap_lines_empty_input():
    result = cap_lines([], max_length=50)
    assert len(result) == 0
    assert result.total_input == 0
    assert result.total_capped == 0


def test_cap_result_capped_ratio():
    lines = [make_line("short", n=1), make_line("a very long message", n=2)]
    result = cap_lines(lines, max_length=8)
    assert result.capped_ratio == pytest.approx(0.5)


def test_cap_result_ratio_empty():
    result = cap_lines([], max_length=10)
    assert result.capped_ratio == 0.0


# --- format_capped ---

def test_format_capped_returns_messages():
    lines = [make_line("hello world extended", n=1), make_line("hi", n=2)]
    result = cap_lines(lines, max_length=10)
    formatted = format_capped(result)
    assert len(formatted) == 2
    assert formatted[1] == "hi"
    assert len(formatted[0]) <= 10

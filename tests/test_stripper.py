"""Tests for logslice.stripper."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

import pytest

from logslice.parser import LogLine
from logslice.stripper import (
    StripResult,
    StrippedLine,
    strip_line,
    strip_lines,
    strip_message,
)


def make_line(
    message: str,
    line_number: int = 1,
    timestamp: Optional[datetime] = None,
    level: Optional[str] = None,
) -> LogLine:
    return LogLine(
        raw=message,
        message=message,
        timestamp=timestamp,
        level=level,
        line_number=line_number,
    )


# --- strip_message ---

def test_strip_message_removes_ansi_color():
    raw = "\x1b[31mERROR\x1b[0m: something failed"
    result = strip_message(raw)
    assert result == "ERROR: something failed"


def test_strip_message_removes_control_chars():
    raw = "hello\x07world\x1f!"
    result = strip_message(raw, remove_ansi=False, remove_control=True)
    assert result == "helloworld!"


def test_strip_message_no_ops_when_both_false():
    raw = "\x1b[32mok\x1b[0m"
    result = strip_message(raw, remove_ansi=False, remove_control=False)
    assert result == raw


def test_strip_message_plain_text_unchanged():
    raw = "plain log message"
    assert strip_message(raw) == raw


def test_strip_message_only_ansi_flag():
    raw = "\x1b[1mbold\x1b[0m\x07beep"
    result = strip_message(raw, remove_ansi=True, remove_control=False)
    assert "bold" in result
    assert "\x1b" not in result
    assert "\x07" in result


# --- strip_line ---

def test_strip_line_was_changed_true_for_ansi():
    line = make_line("\x1b[32mINFO\x1b[0m: started")
    result = strip_line(line)
    assert result.was_changed is True
    assert "INFO: started" == result.message


def test_strip_line_was_changed_false_for_plain():
    line = make_line("plain message")
    result = strip_line(line)
    assert result.was_changed is False
    assert result.message == "plain message"


def test_strip_line_preserves_raw():
    original = "\x1b[31mERROR\x1b[0m"
    line = make_line(original)
    result = strip_line(line)
    assert result.raw == original


def test_strip_line_preserves_line_number():
    line = make_line("msg", line_number=42)
    result = strip_line(line)
    assert result.line_number == 42


def test_strip_line_preserves_timestamp():
    ts = datetime(2024, 1, 1, 12, 0, 0)
    line = make_line("msg", timestamp=ts)
    result = strip_line(line)
    assert result.timestamp == ts


# --- strip_lines ---

def test_strip_lines_returns_strip_result():
    lines = [make_line("\x1b[31mERR\x1b[0m"), make_line("plain")]
    result = strip_lines(lines)
    assert isinstance(result, StripResult)
    assert len(result) == 2


def test_strip_lines_total_changed_count():
    lines = [
        make_line("\x1b[31mERROR\x1b[0m"),
        make_line("no escape"),
        make_line("\x1b[33mWARN\x1b[0m"),
    ]
    result = strip_lines(lines)
    assert result.total_changed == 2


def test_strip_lines_empty_input():
    result = strip_lines([])
    assert len(result) == 0
    assert result.total_changed == 0


def test_strip_lines_all_plain_no_changes():
    lines = [make_line("a"), make_line("b"), make_line("c")]
    result = strip_lines(lines)
    assert result.total_changed == 0

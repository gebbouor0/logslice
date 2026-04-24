"""Tests for logslice/formatter.py"""

from __future__ import annotations

from datetime import datetime

import pytest

from logslice.parser import LogLine
from logslice.formatter import FormatOptions, format_line, format_lines


def make_line(
    msg: str = "hello",
    level: str | None = "INFO",
    ts: datetime | None = None,
    lineno: int = 1,
) -> LogLine:
    return LogLine(
        raw=f"{level} {msg}",
        message=msg,
        timestamp=ts,
        level=level,
        line_number=lineno,
    )


def test_format_line_default_includes_number():
    line = make_line(lineno=7)
    out = format_line(line)
    assert "[7]" in out


def test_format_line_default_no_timestamp_shows_dash():
    line = make_line(ts=None)
    out = format_line(line)
    assert " - " in out or out.split(" | ")[1] == "-"


def test_format_line_with_timestamp():
    ts = datetime(2024, 6, 15, 9, 30, 0)
    line = make_line(ts=ts)
    out = format_line(line)
    assert "2024-06-15 09:30:00" in out


def test_format_line_with_level():
    line = make_line(level="ERROR")
    out = format_line(line)
    assert "ERROR" in out


def test_format_line_no_level_shows_dash():
    line = make_line(level=None)
    out = format_line(line)
    assert " - " in out


def test_format_line_message_always_present():
    line = make_line(msg="something happened")
    out = format_line(line)
    assert "something happened" in out


def test_format_line_hide_line_number():
    opts = FormatOptions(show_line_number=False)
    line = make_line(lineno=42)
    out = format_line(line, opts)
    assert "[42]" not in out


def test_format_line_hide_timestamp():
    ts = datetime(2024, 1, 1)
    opts = FormatOptions(show_timestamp=False)
    line = make_line(ts=ts)
    out = format_line(line, opts)
    assert "2024" not in out


def test_format_line_hide_level():
    opts = FormatOptions(show_level=False)
    line = make_line(level="WARN")
    out = format_line(line, opts)
    assert "WARN" not in out


def test_format_line_custom_separator():
    opts = FormatOptions(separator=" :: ")
    line = make_line(msg="hi")
    out = format_line(line, opts)
    assert " :: " in out


def test_format_line_custom_timestamp_fmt():
    ts = datetime(2024, 3, 5, 14, 0, 0)
    opts = FormatOptions(timestamp_fmt="%d/%m/%Y")
    line = make_line(ts=ts)
    out = format_line(line, opts)
    assert "05/03/2024" in out


def test_format_lines_returns_list():
    lines = [make_line(msg=str(i)) for i in range(4)]
    result = format_lines(lines)
    assert isinstance(result, list)
    assert len(result) == 4


def test_format_lines_empty():
    result = format_lines([])
    assert result == []

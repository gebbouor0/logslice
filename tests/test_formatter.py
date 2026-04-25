"""Tests for logslice.formatter."""
from __future__ import annotations

from datetime import datetime, timezone

from logslice.parser import LogLine
from logslice.formatter import FormatOptions, format_line, format_lines


def make_line(
    msg: str,
    ts: datetime | None = None,
    level: str | None = None,
    n: int = 1,
) -> LogLine:
    return LogLine(raw=msg, line_number=n, timestamp=ts, level=level, message=msg)


def dt() -> datetime:
    return datetime(2024, 3, 15, 12, 0, 0, tzinfo=timezone.utc)


def test_format_line_default_includes_number():
    ln = make_line("hello", n=7)
    out = format_line(ln)
    assert "#7" in out


def test_format_line_default_no_timestamp_shows_dash():
    ln = make_line("hello", ts=None)
    out = format_line(ln)
    assert " | - | " in out or out.startswith("#1 | -")


def test_format_line_with_timestamp():
    ln = make_line("hello", ts=dt())
    out = format_line(ln)
    assert "2024-03-15T12:00:00" in out


def test_format_line_with_level():
    ln = make_line("oops", level="ERROR")
    out = format_line(ln)
    assert "ERROR" in out


def test_format_line_no_level_shows_dash():
    ln = make_line("plain", level=None)
    out = format_line(ln)
    assert " | - | " in out or out.endswith("| -\nplain") or "- | plain" in out


def test_format_line_hide_number():
    opts = FormatOptions(show_line_number=False)
    ln = make_line("msg", n=99)
    out = format_line(ln, opts)
    assert "#99" not in out


def test_format_line_hide_timestamp():
    opts = FormatOptions(show_timestamp=False)
    ln = make_line("msg", ts=dt())
    out = format_line(ln, opts)
    assert "2024" not in out


def test_format_line_hide_level():
    opts = FormatOptions(show_level=False)
    ln = make_line("msg", level="WARNING")
    out = format_line(ln, opts)
    assert "WARNING" not in out


def test_format_line_custom_separator():
    opts = FormatOptions(separator=" :: ")
    ln = make_line("msg")
    out = format_line(ln, opts)
    assert " :: " in out


def test_format_line_custom_timestamp_format():
    opts = FormatOptions(timestamp_format="%H:%M")
    ln = make_line("msg", ts=dt())
    out = format_line(ln, opts)
    assert "12:00" in out
    assert "2024" not in out


def test_format_lines_returns_one_per_line():
    lines = [make_line(f"line {i}", n=i) for i in range(5)]
    out = format_lines(lines)
    assert len(out) == 5


def test_format_lines_empty():
    assert format_lines([]) == []

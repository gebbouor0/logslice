"""Tests for logslice.formatter."""
from datetime import datetime
from logslice.parser import LogLine
from logslice.formatter import FormatOptions, format_line, format_lines


def make_line(msg: str = "hello", n: int = 1, ts=None, level=None) -> LogLine:
    return LogLine(raw=msg, message=msg, timestamp=ts, level=level, line_number=n)


DT = datetime(2024, 3, 15, 12, 0, 0)


def test_format_line_default_includes_number():
    line = make_line("test message", n=5)
    out = format_line(line)
    assert "#5" in out


def test_format_line_default_no_timestamp_shows_dash():
    line = make_line("msg", ts=None)
    out = format_line(line)
    assert " | - | " in out or out.startswith("#1 | -")


def test_format_line_with_timestamp():
    line = make_line("msg", ts=DT)
    out = format_line(line)
    assert "2024-03-15" in out


def test_format_line_with_level():
    line = make_line("msg", level="ERROR")
    out = format_line(line)
    assert "ERROR" in out


def test_format_line_no_level_shows_dash():
    line = make_line("msg", level=None)
    out = format_line(line)
    assert " | - | " in out or out.endswith(" | - | msg")


def test_format_line_message_always_present():
    line = make_line("important log message")
    out = format_line(line)
    assert "important log message" in out


def test_format_line_hide_line_number():
    opts = FormatOptions(show_line_number=False)
    line = make_line("msg", n=99)
    out = format_line(line, opts)
    assert "#99" not in out


def test_format_line_hide_timestamp():
    opts = FormatOptions(show_timestamp=False)
    line = make_line("msg", ts=DT)
    out = format_line(line, opts)
    assert "2024" not in out


def test_format_line_custom_separator():
    opts = FormatOptions(separator=" :: ")
    line = make_line("msg", n=1, ts=DT, level="INFO")
    out = format_line(line, opts)
    assert " :: " in out


def test_format_line_custom_timestamp_format():
    opts = FormatOptions(timestamp_format="%H:%M")
    line = make_line("msg", ts=DT)
    out = format_line(line, opts)
    assert "12:00" in out
    assert "2024" not in out


def test_format_lines_returns_list():
    lines = [make_line(f"msg {i}", n=i) for i in range(4)]
    result = format_lines(lines)
    assert len(result) == 4
    assert all(isinstance(s, str) for s in result)


def test_format_lines_empty():
    assert format_lines([]) == []

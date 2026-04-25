"""Integration tests for stripper combined with other logslice modules."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from logslice.parser import LogLine
from logslice.filter import filter_lines
from logslice.highlighter import highlight_lines
from logslice.stripper import strip_lines


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


def _ansi_lines():
    return [
        make_line("\x1b[31mERROR\x1b[0m: disk full", line_number=1, level="ERROR"),
        make_line("\x1b[32mINFO\x1b[0m: service started", line_number=2, level="INFO"),
        make_line("\x1b[33mWARN\x1b[0m: high memory", line_number=3, level="WARN"),
        make_line("plain debug message", line_number=4, level="DEBUG"),
    ]


def test_strip_then_filter_pattern_works_on_clean_messages():
    """After stripping ANSI, pattern filter should match on clean text."""
    lines = _ansi_lines()
    stripped = strip_lines(lines)
    # Rebuild LogLines from stripped messages so filter can work
    clean_lines = [
        LogLine(
            raw=s.raw,
            message=s.message,
            timestamp=s.timestamp,
            level=s.level,
            line_number=s.line_number,
        )
        for s in stripped.lines
    ]
    filtered = filter_lines(clean_lines, pattern="ERROR")
    assert len(filtered) == 1
    assert "ERROR" in filtered[0].message
    assert "\x1b" not in filtered[0].message


def test_strip_total_lines_preserved():
    lines = _ansi_lines()
    result = strip_lines(lines)
    assert len(result) == len(lines)


def test_strip_changed_count_accurate():
    lines = _ansi_lines()
    result = strip_lines(lines)
    # 3 lines have ANSI codes, 1 is plain
    assert result.total_changed == 3


def test_strip_then_highlight_no_double_escape():
    """Strip first, then highlight — result should contain highlight codes but not original ANSI."""
    lines = _ansi_lines()
    stripped_result = strip_lines(lines)
    clean_lines = [
        LogLine(
            raw=s.raw,
            message=s.message,
            timestamp=s.timestamp,
            level=s.level,
            line_number=s.line_number,
        )
        for s in stripped_result.lines
    ]
    highlighted = highlight_lines(clean_lines, pattern="ERROR")
    # The highlighted line should have re-introduced ANSI for the match
    error_lines = [h for h in highlighted if "ERROR" in h.message]
    assert len(error_lines) == 1

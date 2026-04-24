"""Integration tests: inverter combined with filter/parser utilities."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import List

from logslice.parser import LogLine
from logslice.inverter import invert_lines, format_inverted


def dt(offset_s: int = 0) -> datetime:
    return datetime(2024, 6, 1, 10, 0, 0) + timedelta(seconds=offset_s)


def make_line(message: str, n: int, ts=None) -> LogLine:
    return LogLine(raw=message, line_number=n, timestamp=ts, message=message)


def _mixed_lines() -> List[LogLine]:
    return [
        make_line("INFO service started", 1, dt(0)),
        make_line("DEBUG connecting to db", 2, dt(1)),
        make_line("ERROR connection refused", 3, dt(2)),
        make_line("WARN retry attempt 1", 4, dt(3)),
        make_line("ERROR timeout", 5, dt(4)),
        make_line("INFO recovered", 6, dt(5)),
    ]


def test_invert_errors_leaves_non_errors():
    lines = _mixed_lines()
    result = invert_lines(lines, patterns=["ERROR"])
    messages = [l.message for l in result.kept]
    assert all("ERROR" not in m for m in messages)
    assert len(result.kept) == 4


def test_invert_then_format_length_matches_kept():
    lines = _mixed_lines()
    result = invert_lines(lines, patterns=["DEBUG", "WARN"])
    formatted = format_inverted(result)
    assert len(formatted) == len(result.kept)


def test_invert_preserves_line_numbers():
    lines = _mixed_lines()
    result = invert_lines(lines, patterns=["DEBUG"])
    kept_numbers = [l.line_number for l in result.kept]
    # line 2 is DEBUG and should be dropped
    assert 2 not in kept_numbers
    assert 1 in kept_numbers


def test_invert_all_patterns_drops_all():
    lines = _mixed_lines()
    result = invert_lines(lines, patterns=["INFO", "DEBUG", "ERROR", "WARN"])
    assert len(result.kept) == 0
    assert result.total_input == len(lines)
    assert result.drop_rate == 1.0

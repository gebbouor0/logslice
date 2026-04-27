"""Integration tests combining anchorer with filter and highlighter."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import List

from logslice.parser import LogLine
from logslice.anchorer import anchor_lines, format_anchored
from logslice.filter import filter_lines


def dt(offset: int = 0) -> datetime:
    return datetime(2024, 1, 1, 12, 0, 0) + timedelta(seconds=offset)


def make_line(msg: str, lineno: int = 1, ts=None) -> LogLine:
    return LogLine(raw=msg, message=msg, line_number=lineno, timestamp=ts)


def _mixed_lines() -> List[LogLine]:
    entries = [
        ("INFO app started", 0),
        ("DEBUG loading config", 1),
        ("INFO config loaded", 2),
        ("ERROR failed to connect", 3),
        ("WARNING retrying connection", 4),
        ("INFO connection ok", 5),
        ("ERROR timeout reached", 6),
        ("INFO shutting down", 7),
    ]
    return [make_line(msg, i + 1, dt(off)) for i, (msg, off) in enumerate(entries)]


def test_anchor_error_windows_count():
    lines = _mixed_lines()
    result = anchor_lines(lines, lambda l: "ERROR" in l.message, before=1, after=1)
    assert len(result) == 2


def test_anchor_windows_contain_correct_anchors():
    lines = _mixed_lines()
    result = anchor_lines(lines, lambda l: "ERROR" in l.message, before=1, after=1)
    anchors = [w.anchor.message for w in result.windows]
    assert "ERROR failed to connect" in anchors
    assert "ERROR timeout reached" in anchors


def test_anchor_then_format_total_lines_reasonable():
    lines = _mixed_lines()
    result = anchor_lines(lines, lambda l: "ERROR" in l.message, before=2, after=2)
    output = format_anchored(result)
    # 2 windows * (2 before + anchor + 2 after) + 1 separator = 11
    assert len(output) == 11


def test_anchor_after_filter_only_errors_anchored():
    lines = _mixed_lines()
    filtered = filter_lines(lines, pattern="ERROR|WARNING")
    result = anchor_lines(filtered, lambda l: "ERROR" in l.message, before=1, after=1)
    for window in result.windows:
        assert "ERROR" in window.anchor.message

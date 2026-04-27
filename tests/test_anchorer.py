"""Tests for logslice/anchorer.py."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

import pytest

from logslice.parser import LogLine
from logslice.anchorer import (
    AnchorWindow,
    AnchorResult,
    anchor_lines,
    format_anchored,
)


def make_line(msg: str, lineno: int = 1, ts: Optional[datetime] = None) -> LogLine:
    return LogLine(raw=msg, message=msg, line_number=lineno, timestamp=ts)


def is_error(line: LogLine) -> bool:
    return "ERROR" in line.message


def _make_lines():
    msgs = [
        "INFO start",
        "DEBUG processing",
        "ERROR boom",
        "INFO recovered",
        "DEBUG done",
    ]
    return [make_line(m, i + 1) for i, m in enumerate(msgs)]


def test_anchor_basic_returns_window():
    lines = _make_lines()
    result = anchor_lines(lines, is_error, before=1, after=1)
    assert len(result) == 1
    win = result.windows[0]
    assert win.anchor.message == "ERROR boom"
    assert len(win.before) == 1
    assert win.before[0].message == "DEBUG processing"
    assert len(win.after) == 1
    assert win.after[0].message == "INFO recovered"


def test_anchor_total_input_set():
    lines = _make_lines()
    result = anchor_lines(lines, is_error)
    assert result.total_input == len(lines)


def test_anchor_no_match_returns_empty():
    lines = _make_lines()
    result = anchor_lines(lines, lambda l: "CRITICAL" in l.message)
    assert len(result) == 0
    assert result.total_input == 5


def test_anchor_clamps_at_stream_start():
    lines = _make_lines()
    result = anchor_lines(lines, lambda l: l.line_number == 1, before=5, after=1)
    win = result.windows[0]
    assert win.before == []
    assert len(win.after) == 1


def test_anchor_clamps_at_stream_end():
    lines = _make_lines()
    result = anchor_lines(lines, lambda l: l.line_number == 5, before=1, after=10)
    win = result.windows[0]
    assert len(win.before) == 1
    assert win.after == []


def test_anchor_window_len_includes_anchor():
    lines = _make_lines()
    result = anchor_lines(lines, is_error, before=2, after=2)
    win = result.windows[0]
    assert len(win) == 5


def test_anchor_all_lines_order():
    lines = _make_lines()
    result = anchor_lines(lines, is_error, before=1, after=1)
    all_lines = result.windows[0].all_lines
    assert [l.message for l in all_lines] == [
        "DEBUG processing",
        "ERROR boom",
        "INFO recovered",
    ]


def test_anchor_multiple_matches():
    lines = [
        make_line("ERROR first", 1),
        make_line("INFO mid", 2),
        make_line("ERROR second", 3),
    ]
    result = anchor_lines(lines, is_error, before=0, after=0)
    assert len(result) == 2


def test_anchor_invalid_before_raises():
    with pytest.raises(ValueError):
        anchor_lines([], is_error, before=-1, after=0)


def test_anchor_invalid_after_raises():
    with pytest.raises(ValueError):
        anchor_lines([], is_error, before=0, after=-1)


def test_format_anchored_marker():
    lines = _make_lines()
    result = anchor_lines(lines, is_error, before=1, after=1)
    output = format_anchored(result)
    assert any(line.startswith(">>> ") for line in output)
    assert any(line.startswith("    ") for line in output)


def test_format_anchored_separator_between_windows():
    lines = [
        make_line("ERROR first", 1),
        make_line("INFO mid", 2),
        make_line("ERROR second", 3),
    ]
    result = anchor_lines(lines, is_error, before=0, after=0)
    output = format_anchored(result, separator="---")
    assert "---" in output


def test_format_anchored_empty_result():
    result = AnchorResult(total_input=0)
    assert format_anchored(result) == []

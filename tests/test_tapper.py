"""Tests for logslice/tapper.py"""

from __future__ import annotations

from datetime import datetime
from typing import List

import pytest

from logslice.parser import LogLine
from logslice.tapper import TapResult, format_tap_summary, tap_lines


def make_line(msg: str, level: str = "INFO", ts: datetime | None = None) -> LogLine:
    return LogLine(
        raw=f"{level} {msg}",
        message=msg,
        timestamp=ts,
        level=level,
        line_number=1,
    )


# ---------------------------------------------------------------------------
# tap_lines — basic pass-through
# ---------------------------------------------------------------------------

def test_tap_returns_all_lines():
    lines = [make_line("a"), make_line("b"), make_line("c")]
    result = tap_lines(lines, callback=lambda _: None)
    assert len(result) == 3


def test_tap_preserves_order():
    lines = [make_line(str(i)) for i in range(5)]
    result = tap_lines(lines, callback=lambda _: None)
    assert [l.message for l in result] == [str(i) for i in range(5)]


def test_tap_callback_called_for_all_lines_no_predicate():
    seen: List[str] = []
    lines = [make_line("x"), make_line("y")]
    tap_lines(lines, callback=lambda l: seen.append(l.message))
    assert seen == ["x", "y"]


def test_tap_count_equals_total_without_predicate():
    lines = [make_line("a"), make_line("b"), make_line("c")]
    result = tap_lines(lines, callback=lambda _: None)
    assert result.tap_count == 3


# ---------------------------------------------------------------------------
# tap_lines — with predicate
# ---------------------------------------------------------------------------

def test_tap_predicate_filters_callback():
    seen: List[str] = []
    lines = [make_line("ok", "INFO"), make_line("boom", "ERROR")]
    tap_lines(
        lines,
        callback=lambda l: seen.append(l.message),
        predicate=lambda l: l.level == "ERROR",
    )
    assert seen == ["boom"]


def test_tap_predicate_still_passes_all_lines_through():
    lines = [make_line("ok", "INFO"), make_line("boom", "ERROR")]
    result = tap_lines(
        lines,
        callback=lambda _: None,
        predicate=lambda l: l.level == "ERROR",
    )
    assert len(result) == 2


def test_tap_count_reflects_predicate_matches():
    lines = [make_line("a", "INFO"), make_line("b", "WARN"), make_line("c", "ERROR")]
    result = tap_lines(
        lines,
        callback=lambda _: None,
        predicate=lambda l: l.level in ("WARN", "ERROR"),
    )
    assert result.tap_count == 2


def test_tap_empty_input():
    result = tap_lines([], callback=lambda _: None)
    assert len(result) == 0
    assert result.tap_count == 0


# ---------------------------------------------------------------------------
# format_tap_summary
# ---------------------------------------------------------------------------

def test_format_tap_summary_all_tapped():
    lines = [make_line("x"), make_line("y")]
    result = tap_lines(lines, callback=lambda _: None)
    summary = format_tap_summary(result)
    assert "2/2" in summary
    assert "100.0%" in summary


def test_format_tap_summary_none_tapped():
    lines = [make_line("x"), make_line("y")]
    result = tap_lines(lines, callback=lambda _: None, predicate=lambda _: False)
    summary = format_tap_summary(result)
    assert "0/2" in summary


def test_format_tap_summary_empty():
    result = tap_lines([], callback=lambda _: None)
    summary = format_tap_summary(result)
    assert "0/0" in summary


def test_tap_result_iterable():
    lines = [make_line("a"), make_line("b")]
    result = tap_lines(lines, callback=lambda _: None)
    messages = [l.message for l in result]
    assert messages == ["a", "b"]

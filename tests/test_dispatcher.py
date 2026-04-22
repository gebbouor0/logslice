"""Tests for logslice.dispatcher."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

import pytest

from logslice.parser import LogLine
from logslice.dispatcher import (
    DispatchRule,
    DispatchResult,
    dispatch_lines,
    format_dispatch_summary,
)


def make_line(
    message: str,
    level: Optional[str] = None,
    ts: Optional[datetime] = None,
    n: int = 1,
) -> LogLine:
    return LogLine(raw=message, line_number=n, timestamp=ts, level=level, message=message)


def is_error(line: LogLine) -> bool:
    return (line.level or "").upper() == "ERROR"


def is_warning(line: LogLine) -> bool:
    return (line.level or "").upper() == "WARNING"


def test_dispatch_single_rule_matches():
    lines = [make_line("boom", level="ERROR"), make_line("ok", level="INFO")]
    rules = [DispatchRule(queue="errors", predicate=is_error)]
    result = dispatch_lines(lines, rules)
    assert len(result.get("errors")) == 1
    assert result.get("errors")[0].message == "boom"


def test_dispatch_unmatched_goes_to_unmatched():
    lines = [make_line("ok", level="INFO")]
    rules = [DispatchRule(queue="errors", predicate=is_error)]
    result = dispatch_lines(lines, rules)
    assert len(result.unmatched) == 1
    assert result.get("errors") == []


def test_dispatch_default_queue_captures_unmatched():
    lines = [make_line("ok", level="INFO")]
    rules = [DispatchRule(queue="errors", predicate=is_error)]
    result = dispatch_lines(lines, rules, default_queue="misc")
    assert len(result.get("misc")) == 1
    assert result.unmatched == []


def test_dispatch_stop_on_match_prevents_double_routing():
    lines = [make_line("bad", level="ERROR")]
    rules = [
        DispatchRule(queue="errors", predicate=is_error, stop_on_match=True),
        DispatchRule(queue="all", predicate=lambda _: True, stop_on_match=False),
    ]
    result = dispatch_lines(lines, rules)
    assert len(result.get("errors")) == 1
    assert result.get("all") == []


def test_dispatch_no_stop_on_match_allows_multi_queue():
    lines = [make_line("bad", level="ERROR")]
    rules = [
        DispatchRule(queue="errors", predicate=is_error, stop_on_match=False),
        DispatchRule(queue="all", predicate=lambda _: True, stop_on_match=False),
    ]
    result = dispatch_lines(lines, rules)
    assert len(result.get("errors")) == 1
    assert len(result.get("all")) == 1


def test_dispatch_multiple_rules_first_wins_with_stop():
    lines = [make_line("warn", level="WARNING")]
    rules = [
        DispatchRule(queue="warnings", predicate=is_warning, stop_on_match=True),
        DispatchRule(queue="errors", predicate=is_error, stop_on_match=True),
    ]
    result = dispatch_lines(lines, rules)
    assert len(result.get("warnings")) == 1
    assert result.get("errors") == []


def test_dispatch_empty_input():
    result = dispatch_lines([], [DispatchRule(queue="errors", predicate=is_error)])
    assert len(result) == 0
    assert result.unmatched == []


def test_dispatch_queue_names():
    lines = [make_line("e", level="ERROR"), make_line("w", level="WARNING")]
    rules = [
        DispatchRule(queue="errors", predicate=is_error),
        DispatchRule(queue="warnings", predicate=is_warning),
    ]
    result = dispatch_lines(lines, rules)
    assert set(result.queue_names) == {"errors", "warnings"}


def test_format_dispatch_summary_basic():
    lines = [make_line("e", level="ERROR"), make_line("ok", level="INFO")]
    rules = [DispatchRule(queue="errors", predicate=is_error)]
    result = dispatch_lines(lines, rules)
    summary = format_dispatch_summary(result)
    assert "errors" in summary
    assert "unmatched" in summary


def test_format_dispatch_summary_empty():
    result = DispatchResult()
    summary = format_dispatch_summary(result)
    assert summary == "No lines dispatched."

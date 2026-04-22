"""Integration tests for dispatcher — combines with parser/filter concepts."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from logslice.parser import LogLine
from logslice.dispatcher import DispatchRule, dispatch_lines, format_dispatch_summary


def dt(h: int, m: int = 0) -> datetime:
    return datetime(2024, 1, 1, h, m)


def make_line(
    message: str,
    level: Optional[str] = None,
    ts: Optional[datetime] = None,
    n: int = 1,
) -> LogLine:
    return LogLine(raw=message, line_number=n, timestamp=ts, level=level, message=message)


def _make_mixed_lines():
    return [
        make_line("started", level="INFO", ts=dt(9), n=1),
        make_line("disk full", level="ERROR", ts=dt(9, 5), n=2),
        make_line("retrying", level="WARNING", ts=dt(9, 10), n=3),
        make_line("connected", level="INFO", ts=dt(9, 15), n=4),
        make_line("timeout", level="ERROR", ts=dt(9, 20), n=5),
    ]


def test_total_lines_preserved_across_queues():
    lines = _make_mixed_lines()
    rules = [
        DispatchRule(queue="errors", predicate=lambda l: (l.level or "").upper() == "ERROR"),
        DispatchRule(queue="warnings", predicate=lambda l: (l.level or "").upper() == "WARNING"),
        DispatchRule(queue="info", predicate=lambda l: (l.level or "").upper() == "INFO"),
    ]
    result = dispatch_lines(lines, rules)
    total = sum(len(result.get(q)) for q in result.queue_names) + len(result.unmatched)
    assert total == len(lines)


def test_error_queue_has_correct_messages():
    lines = _make_mixed_lines()
    rules = [
        DispatchRule(queue="errors", predicate=lambda l: (l.level or "").upper() == "ERROR"),
    ]
    result = dispatch_lines(lines, rules, default_queue="other")
    error_messages = [l.message for l in result.get("errors")]
    assert "disk full" in error_messages
    assert "timeout" in error_messages
    assert "started" not in error_messages


def test_format_summary_lists_all_queues():
    lines = _make_mixed_lines()
    rules = [
        DispatchRule(queue="errors", predicate=lambda l: (l.level or "").upper() == "ERROR", stop_on_match=False),
        DispatchRule(queue="all", predicate=lambda _: True, stop_on_match=False),
    ]
    result = dispatch_lines(lines, rules)
    summary = format_dispatch_summary(result)
    assert "errors" in summary
    assert "all" in summary


def test_dispatch_preserves_line_order_within_queue():
    lines = [
        make_line("first error", level="ERROR", n=1),
        make_line("second error", level="ERROR", n=2),
        make_line("third error", level="ERROR", n=3),
    ]
    rules = [DispatchRule(queue="errors", predicate=lambda l: True)]
    result = dispatch_lines(lines, rules)
    numbers = [l.line_number for l in result.get("errors")]
    assert numbers == [1, 2, 3]

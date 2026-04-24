"""Integration tests: tap_lines interacting with other logslice modules."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import List

from logslice.parser import LogLine
from logslice.tapper import tap_lines
from logslice.filter import filter_lines
from logslice.stats import compute_stats


def make_line(
    msg: str,
    level: str = "INFO",
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


def dt(offset: int = 0) -> datetime:
    return datetime(2024, 1, 1, 12, 0, 0) + timedelta(seconds=offset)


def test_tap_then_filter_preserves_all_for_filter():
    """Tapping should not affect what filter_lines sees."""
    lines = [
        make_line("alpha", ts=dt(0)),
        make_line("beta", ts=dt(10)),
        make_line("gamma", ts=dt(20)),
    ]
    tapped: List[LogLine] = []
    result = tap_lines(lines, callback=lambda l: tapped.append(l))
    filtered = filter_lines(list(result), start=dt(5), end=dt(25))
    assert len(filtered) == 2
    assert len(tapped) == 3  # tap saw everything


def test_tap_side_effect_accumulates_errors():
    """Collect ERROR lines via tap, then verify count matches stats."""
    lines = [
        make_line("ok", level="INFO"),
        make_line("bad", level="ERROR"),
        make_line("also bad", level="ERROR"),
        make_line("fine", level="INFO"),
    ]
    errors: List[LogLine] = []
    result = tap_lines(
        lines,
        callback=lambda l: errors.append(l),
        predicate=lambda l: l.level == "ERROR",
    )
    stats = compute_stats(list(result))
    assert result.tap_count == 2
    assert len(errors) == 2
    assert stats.level_counts.get("ERROR", 0) == 2


def test_tap_does_not_mutate_original_lines():
    """Lines yielded by tap_lines should be the same objects (no copy)."""
    original = [make_line("x", lineno=i) for i in range(4)]
    result = tap_lines(original, callback=lambda _: None)
    for orig, tapped in zip(original, result.lines):
        assert orig is tapped

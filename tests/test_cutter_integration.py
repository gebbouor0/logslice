"""Integration tests: cutter combined with filter and formatter."""
from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import List

from logslice.parser import LogLine
from logslice.cutter import cut_lines, format_cut
from logslice.filter import filter_lines


def dt(offset_s: int = 0) -> datetime:
    base = datetime(2024, 6, 1, 10, 0, 0, tzinfo=timezone.utc)
    return base + timedelta(seconds=offset_s)


def make_line(n: int, msg: str, ts: datetime | None = None) -> LogLine:
    return LogLine(raw=msg, line_number=n, timestamp=ts, message=msg)


def _mixed_lines() -> List[LogLine]:
    return [
        make_line(1, "INFO startup", dt(0)),
        make_line(2, "ERROR disk full", dt(5)),
        make_line(3, "INFO heartbeat", dt(10)),
        make_line(4, "WARNING memory high", dt(15)),
        make_line(5, "ERROR timeout", dt(20)),
        make_line(6, "INFO shutdown", dt(25)),
    ]


def test_cut_then_filter_reduces_set():
    lines = _mixed_lines()
    cut = cut_lines(lines, start=1, end=5)  # lines 2-5
    filtered = filter_lines(cut.lines, pattern="ERROR")
    assert all("ERROR" in l.message for l in filtered)
    assert len(filtered) <= len(cut)


def test_cut_preserves_total_input_metadata():
    lines = _mixed_lines()
    result = cut_lines(lines, start=2, end=4)
    assert result.total_input == len(lines)
    assert result.dropped_head + len(result) + result.dropped_tail == result.total_input


def test_format_cut_line_count_matches_result():
    lines = _mixed_lines()
    result = cut_lines(lines, start=0, end=3)
    formatted = format_cut(result)
    assert len(formatted) == len(result)


def test_cut_full_range_equals_all_lines():
    lines = _mixed_lines()
    result = cut_lines(lines)
    assert len(result) == len(lines)
    assert result.dropped_head == 0
    assert result.dropped_tail == 0

"""Integration tests for splitter3 combined with filter/formatter."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from logslice.parser import LogLine
from logslice.splitter3 import format_keyword_segments, split_by_keyword


def make_line(msg: str, n: int = 1, ts: Optional[datetime] = None) -> LogLine:
    return LogLine(raw=msg, message=msg, line_number=n, timestamp=ts, level=None)


def _transaction_log():
    return [
        make_line("system ready", 1),
        make_line("BEGIN txn-1", 2),
        make_line("INSERT row", 3),
        make_line("COMMIT txn-1", 4),
        make_line("idle", 5),
        make_line("BEGIN txn-2", 6),
        make_line("DELETE row", 7),
        make_line("COMMIT txn-2", 8),
    ]


def test_begin_creates_new_segment_each_occurrence():
    lines = _transaction_log()
    result = split_by_keyword(lines, keywords=["BEGIN"])
    begin_segs = [s for s in result.segments if s.name == "BEGIN"]
    assert len(begin_segs) == 2


def test_total_input_matches_all_lines():
    lines = _transaction_log()
    result = split_by_keyword(lines, keywords=["BEGIN", "COMMIT"])
    assert result.total_input == len(lines)


def test_format_non_empty_for_non_empty_input():
    lines = _transaction_log()
    result = split_by_keyword(lines, keywords=["BEGIN"])
    out = format_keyword_segments(result)
    assert len(out) > 0


def test_segment_lines_sum_equals_total_with_boundary():
    lines = _transaction_log()
    result = split_by_keyword(lines, keywords=["BEGIN", "COMMIT"], include_boundary=True)
    assert result.total_lines == len(lines)


def test_segment_lines_sum_less_without_boundary():
    lines = _transaction_log()
    result = split_by_keyword(lines, keywords=["BEGIN", "COMMIT"], include_boundary=False)
    # boundary lines are dropped, so total_lines < total_input
    boundary_count = sum(1 for l in lines if "BEGIN" in l.message or "COMMIT" in l.message)
    assert result.total_lines == len(lines) - boundary_count

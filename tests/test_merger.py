"""Tests for logslice.merger."""

from datetime import datetime, timezone
from typing import List

import pytest

from logslice.parser import LogLine
from logslice.merger import SourcedLine, merge_streams, format_merged


def make_line(raw: str, ts: datetime | None = None, ln: int = 0) -> LogLine:
    return LogLine(raw=raw, timestamp=ts, level=None, message=raw, line_number=ln)


def dt(hour: int, minute: int = 0) -> datetime:
    return datetime(2024, 1, 1, hour, minute, tzinfo=timezone.utc)


def test_merge_streams_ordering():
    a = [make_line("a1", dt(10, 0), 0), make_line("a2", dt(10, 30), 1)]
    b = [make_line("b1", dt(10, 15), 0), make_line("b2", dt(11, 0), 1)]
    result = merge_streams([("A", a), ("B", b)])
    texts = [sl.line.raw for sl in result]
    assert texts == ["a1", "b1", "a2", "b2"]


def test_merge_streams_source_labels():
    a = [make_line("x", dt(9), 0)]
    b = [make_line("y", dt(8), 0)]
    result = merge_streams([("src_a", a), ("src_b", b)])
    assert result[0].source == "src_b"
    assert result[1].source == "src_a"


def test_merge_streams_empty():
    result = merge_streams([])
    assert result == []


def test_merge_streams_single_stream():
    lines = [make_line(f"l{i}", dt(i), i) for i in range(3)]
    result = merge_streams([("only", lines)])
    assert len(result) == 3
    assert all(sl.source == "only" for sl in result)


def test_merge_streams_no_timestamps_fallback_to_line_number():
    a = [make_line("a", None, 2), make_line("b", None, 5)]
    b = [make_line("c", None, 1), make_line("d", None, 3)]
    result = merge_streams([("A", a), ("B", b)])
    line_numbers = [sl.line.line_number for sl in result]
    assert line_numbers == sorted(line_numbers)


def test_merge_streams_mixed_timestamps():
    """Lines without timestamps should sort after timestamped ones."""
    a = [make_line("ts", dt(10), 0)]
    b = [make_line("no_ts", None, 0)]
    result = merge_streams([("A", a), ("B", b)])
    assert result[0].line.raw == "ts"
    assert result[1].line.raw == "no_ts"


def test_format_merged_with_source():
    lines = [make_line("hello", dt(10), 0)]
    sourced = [SourcedLine(line=lines[0], source="app")]
    out = format_merged(sourced, show_source=True)
    assert out == ["[app] hello"]


def test_format_merged_without_source():
    lines = [make_line("hello", dt(10), 0)]
    sourced = [SourcedLine(line=lines[0], source="app")]
    out = format_merged(sourced, show_source=False)
    assert out == ["hello"]


def test_format_merged_empty():
    assert format_merged([]) == []

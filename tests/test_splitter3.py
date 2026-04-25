"""Tests for logslice.splitter3."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

import pytest

from logslice.parser import LogLine
from logslice.splitter3 import (
    KeywordSegment,
    KeywordSplitResult,
    format_keyword_segments,
    split_by_keyword,
)


def make_line(msg: str, n: int = 1, ts: Optional[datetime] = None) -> LogLine:
    return LogLine(raw=msg, message=msg, line_number=n, timestamp=ts, level=None)


def test_split_empty_input():
    result = split_by_keyword([], keywords=["START"])
    assert len(result) == 0
    assert result.total_input == 0


def test_split_no_keyword_match():
    lines = [make_line("hello", 1), make_line("world", 2)]
    result = split_by_keyword(lines, keywords=["START"])
    assert len(result) == 1
    assert result.segments[0].name == "preamble"
    assert len(result.segments[0]) == 2


def test_split_single_keyword_creates_two_segments():
    lines = [
        make_line("before", 1),
        make_line("START here", 2),
        make_line("after", 3),
    ]
    result = split_by_keyword(lines, keywords=["START"])
    assert len(result) == 2
    assert result.segments[0].name == "preamble"
    assert result.segments[1].name == "START"


def test_split_boundary_line_included_by_default():
    lines = [make_line("START here", 1), make_line("body", 2)]
    result = split_by_keyword(lines, keywords=["START"])
    seg = result.segments[0]
    assert any("START" in l.message for l in seg.lines)


def test_split_boundary_excluded_when_flag_false():
    lines = [make_line("START here", 1), make_line("body", 2)]
    result = split_by_keyword(lines, keywords=["START"], include_boundary=False)
    seg = result.segments[0]
    assert all("START" not in l.message for l in seg.lines)


def test_split_case_insensitive_default():
    lines = [make_line("start here", 1), make_line("body", 2)]
    result = split_by_keyword(lines, keywords=["START"])
    # case-insensitive: 'start' should match 'START'
    assert any(s.name == "START" for s in result.segments)


def test_split_case_sensitive_no_match():
    lines = [make_line("start here", 1)]
    result = split_by_keyword(lines, keywords=["START"], case_sensitive=True)
    assert len(result) == 1
    assert result.segments[0].name == "preamble"


def test_split_total_lines_preserved():
    lines = [
        make_line("a", 1),
        make_line("START", 2),
        make_line("b", 3),
        make_line("END", 4),
        make_line("c", 5),
    ]
    result = split_by_keyword(lines, keywords=["START", "END"])
    assert result.total_lines == len(lines)


def test_format_keyword_segments_output():
    lines = [make_line("START", 1), make_line("body", 2)]
    result = split_by_keyword(lines, keywords=["START"])
    out = format_keyword_segments(result)
    assert any("START" in line for line in out)
    assert any("body" in line for line in out)


def test_split_custom_default_name():
    lines = [make_line("hello", 1)]
    result = split_by_keyword(lines, keywords=["X"], default_name="intro")
    assert result.segments[0].name == "intro"

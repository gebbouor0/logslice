"""Tests for logslice/fencer.py."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

import pytest

from logslice.parser import LogLine
from logslice.fencer import fence_lines, format_fenced, FencedBlock


def make_line(msg: str, n: int = 1, ts: Optional[datetime] = None) -> LogLine:
    return LogLine(raw=msg, message=msg, line_number=n, timestamp=ts, level=None)


def test_fence_basic_block():
    lines = [
        make_line("before", 1),
        make_line("START here", 2),
        make_line("inside 1", 3),
        make_line("inside 2", 4),
        make_line("END here", 5),
        make_line("after", 6),
    ]
    result = fence_lines(lines, r"START", r"END")
    assert len(result) == 1
    assert result.total_input == 6
    assert result.blocks[0].is_closed


def test_fence_includes_fence_lines_by_default():
    lines = [
        make_line("START", 1),
        make_line("middle", 2),
        make_line("END", 3),
    ]
    result = fence_lines(lines, r"START", r"END", include_fences=True)
    assert len(result.blocks[0]) == 3


def test_fence_excludes_fence_lines_when_flag_false():
    lines = [
        make_line("START", 1),
        make_line("middle", 2),
        make_line("END", 3),
    ]
    result = fence_lines(lines, r"START", r"END", include_fences=False)
    assert len(result.blocks[0]) == 1
    assert result.blocks[0].lines[0].message == "middle"


def test_fence_multiple_blocks():
    lines = [
        make_line("START", 1),
        make_line("a", 2),
        make_line("END", 3),
        make_line("START", 4),
        make_line("b", 5),
        make_line("END", 6),
    ]
    result = fence_lines(lines, r"START", r"END", include_fences=False)
    assert len(result) == 2
    assert result.blocks[0].lines[0].message == "a"
    assert result.blocks[1].lines[0].message == "b"


def test_fence_unclosed_block():
    lines = [
        make_line("START", 1),
        make_line("data", 2),
    ]
    result = fence_lines(lines, r"START", r"END")
    assert len(result) == 1
    assert not result.blocks[0].is_closed


def test_fence_no_match_returns_empty():
    lines = [make_line("nothing", i) for i in range(1, 4)]
    result = fence_lines(lines, r"START", r"END")
    assert len(result) == 0
    assert result.total_captured == 0


def test_fence_empty_input():
    result = fence_lines([], r"START", r"END")
    assert result.total_input == 0
    assert len(result) == 0


def test_fence_total_captured():
    lines = [
        make_line("START", 1),
        make_line("x", 2),
        make_line("y", 3),
        make_line("END", 4),
    ]
    result = fence_lines(lines, r"START", r"END", include_fences=False)
    assert result.total_captured == 2


def test_format_fenced_no_blocks():
    from logslice.fencer import FenceResult
    result = FenceResult(blocks=[], total_input=3)
    out = format_fenced(result)
    assert "no fenced blocks" in out


def test_format_fenced_shows_block_info():
    lines = [
        make_line("START", 1),
        make_line("hello", 2),
        make_line("END", 3),
    ]
    result = fence_lines(lines, r"START", r"END", include_fences=False)
    out = format_fenced(result)
    assert "block 1" in out
    assert "hello" in out

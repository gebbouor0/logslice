"""Tests for logslice.splitter."""
import pytest
from logslice.parser import LogLine
from logslice.splitter import (
    Segment,
    split_by_pattern,
    split_by_size,
    format_segments,
)


def make_line(msg: str, n: int = 1) -> LogLine:
    raw = f"2024-01-01T00:00:0{n} INFO {msg}"
    return LogLine(raw=raw, timestamp=None, message=msg, line_number=n)


def test_split_by_pattern_basic():
    lines = [
        make_line("startup", 1),
        make_line("--- section A ---", 2),
        make_line("doing stuff", 3),
        make_line("--- section B ---", 4),
        make_line("more stuff", 5),
    ]
    segs = split_by_pattern(lines, r"--- section")
    assert len(segs) == 3
    assert segs[0].lines[0].message == "startup"
    assert len(segs[1]) == 2
    assert len(segs[2]) == 2


def test_split_by_pattern_no_match():
    lines = [make_line("a", 1), make_line("b", 2)]
    segs = split_by_pattern(lines, r"NEVER")
    assert len(segs) == 1
    assert len(segs[0]) == 2


def test_split_by_pattern_empty():
    assert split_by_pattern([], r"x") == []


def test_split_by_pattern_default_name():
    lines = [make_line("pre", 1), make_line("MARK", 2)]
    segs = split_by_pattern(lines, r"MARK", default_name="preamble")
    assert segs[0].name == "preamble"


def test_split_by_size_basic():
    lines = [make_line(f"msg{i}", i) for i in range(7)]
    segs = split_by_size(lines, 3)
    assert len(segs) == 3
    assert len(segs[0]) == 3
    assert len(segs[1]) == 3
    assert len(segs[2]) == 1


def test_split_by_size_exact():
    lines = [make_line(f"m{i}", i) for i in range(6)]
    segs = split_by_size(lines, 2)
    assert len(segs) == 3


def test_split_by_size_invalid():
    with pytest.raises(ValueError):
        split_by_size([], 0)


def test_split_by_size_names():
    lines = [make_line("x", i) for i in range(4)]
    segs = split_by_size(lines, 2)
    assert segs[0].name == "segment-1"
    assert segs[1].name == "segment-2"


def test_format_segments_output():
    lines = [make_line("hello", 1), make_line("world", 2)]
    segs = split_by_size(lines, 2)
    out = format_segments(segs)
    assert any("segment-1" in l for l in out)
    assert any("hello" in l for l in out)


def test_format_segments_custom_separator():
    lines = [make_line("a", 1)]
    segs = split_by_size(lines, 1)
    out = format_segments(segs, separator="===")
    assert out[0].startswith("===")


def test_segment_len():
    s = Segment(name="test", lines=[make_line("a", 1), make_line("b", 2)])
    assert len(s) == 2

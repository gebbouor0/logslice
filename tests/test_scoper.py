import pytest
from logslice.parser import LogLine
from logslice.scoper import ScopedBlock, scope_lines, format_scoped


def make_line(n: int, msg: str) -> LogLine:
    return LogLine(raw=msg, line_number=n, timestamp=None, message=msg)


def is_error(line: LogLine) -> bool:
    return "ERROR" in line.message


def make_lines(messages):
    return [make_line(i + 1, m) for i, m in enumerate(messages)]


def test_scope_basic_returns_block():
    lines = make_lines(["a", "b", "ERROR here", "d", "e"])
    blocks = scope_lines(lines, is_error, before=1, after=1)
    assert len(blocks) == 1
    assert len(blocks[0].lines) == 3


def test_scope_anchor_is_matched_line():
    lines = make_lines(["a", "ERROR here", "c"])
    blocks = scope_lines(lines, is_error, before=1, after=1)
    assert blocks[0].anchor.message == "ERROR here"


def test_scope_clamps_at_start():
    lines = make_lines(["ERROR here", "b", "c"])
    blocks = scope_lines(lines, is_error, before=5, after=1)
    assert blocks[0].lines[0].line_number == 1


def test_scope_clamps_at_end():
    lines = make_lines(["a", "b", "ERROR here"])
    blocks = scope_lines(lines, is_error, before=1, after=5)
    assert blocks[0].lines[-1].line_number == 3


def test_scope_no_match_returns_empty():
    lines = make_lines(["a", "b", "c"])
    blocks = scope_lines(lines, is_error)
    assert blocks == []


def test_scope_multiple_matches():
    lines = make_lines(["ERROR one", "mid", "ERROR two"])
    blocks = scope_lines(lines, is_error, before=0, after=0)
    assert len(blocks) == 2


def test_scope_invalid_before_raises():
    lines = make_lines(["a"])
    with pytest.raises(ValueError):
        scope_lines(lines, is_error, before=-1)


def test_scope_invalid_after_raises():
    lines = make_lines(["a"])
    with pytest.raises(ValueError):
        scope_lines(lines, is_error, after=-1)


def test_format_scoped_marker():
    lines = make_lines(["before", "ERROR x", "after"])
    blocks = scope_lines(lines, is_error, before=1, after=1)
    out = format_scoped(blocks)
    assert any(">> " in l and "ERROR x" in l for l in out)
    assert any("   " in l and "before" in l for l in out)


def test_format_scoped_separator():
    lines = make_lines(["ERROR a", "mid", "ERROR b"])
    blocks = scope_lines(lines, is_error, before=0, after=0)
    out = format_scoped(blocks, separator="===")
    assert "===" in out

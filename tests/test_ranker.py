import pytest
from logslice.parser import LogLine
from logslice.ranker import rank_by_pattern, rank_by_field, format_rank, RankResult


def make_line(msg: str, level: str = "INFO", lineno: int = 1) -> LogLine:
    return LogLine(raw=msg, message=msg, timestamp=None, level=level, line_number=lineno)


def test_rank_by_pattern_basic():
    lines = [
        make_line("error code=500"),
        make_line("error code=500"),
        make_line("warn code=404"),
    ]
    result = rank_by_pattern(lines, r"code=\d+")
    assert len(result) == 2
    top = result.top(10)
    assert top[0].value == "code=500"
    assert top[0].count == 2


def test_rank_by_pattern_no_match():
    lines = [make_line("hello world")]
    result = rank_by_pattern(lines, r"code=\d+")
    assert len(result) == 0


def test_rank_by_pattern_empty():
    result = rank_by_pattern([], r"\w+")
    assert len(result) == 0


def test_rank_by_field_level():
    lines = [
        make_line("a", level="ERROR"),
        make_line("b", level="ERROR"),
        make_line("c", level="INFO"),
    ]
    result = rank_by_field(lines, "level")
    top = result.top()
    assert top[0].value == "ERROR"
    assert top[0].count == 2


def test_rank_by_field_missing_attr():
    lines = [make_line("x")]
    result = rank_by_field(lines, "nonexistent_field")
    assert len(result) == 0


def test_rank_bottom():
    lines = [
        make_line("x=1"), make_line("x=1"), make_line("x=1"),
        make_line("x=2"),
    ]
    result = rank_by_pattern(lines, r"x=\d")
    bottom = result.bottom(1)
    assert bottom[0].value == "x=2"
    assert bottom[0].count == 1


def test_format_rank_basic():
    lines = [make_line("code=200"), make_line("code=200"), make_line("code=404")]
    result = rank_by_pattern(lines, r"code=\d+")
    output = format_rank(result, n=5)
    assert "code=200" in output
    assert "2" in output


def test_format_rank_empty():
    result = RankResult()
    assert format_rank(result) == "(no results)"


def test_rank_lines_stored():
    l1 = make_line("err=timeout", lineno=1)
    l2 = make_line("err=timeout", lineno=2)
    result = rank_by_pattern([l1, l2], r"err=\w+")
    assert len(result.entries[0].lines) == 2

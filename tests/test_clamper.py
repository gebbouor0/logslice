import pytest
from logslice.parser import LogLine
from logslice.clamper import clamp_head, clamp_tail, clamp_lines, format_clamp


def make_line(n: int, msg: str = "msg") -> LogLine:
    return LogLine(raw=f"{msg} {n}", timestamp=None, message=f"{msg} {n}", line_number=n)


def make_lines(count: int) -> list:
    return [make_line(i) for i in range(1, count + 1)]


def test_clamp_head_basic():
    lines = make_lines(10)
    result = clamp_head(lines, 3)
    assert len(result) == 3
    assert result.lines[0].line_number == 1
    assert result.lines[-1].line_number == 3


def test_clamp_head_more_than_available():
    lines = make_lines(5)
    result = clamp_head(lines, 20)
    assert len(result) == 5
    assert result.dropped == 0


def test_clamp_head_zero():
    lines = make_lines(5)
    result = clamp_head(lines, 0)
    assert len(result) == 0
    assert result.dropped == 5


def test_clamp_tail_basic():
    lines = make_lines(10)
    result = clamp_tail(lines, 4)
    assert len(result) == 4
    assert result.lines[0].line_number == 7
    assert result.lines[-1].line_number == 10


def test_clamp_tail_zero():
    lines = make_lines(5)
    result = clamp_tail(lines, 0)
    assert len(result) == 0


def test_clamp_tail_more_than_available():
    lines = make_lines(3)
    result = clamp_tail(lines, 100)
    assert len(result) == 3


def test_clamp_lines_head_mode():
    lines = make_lines(8)
    result = clamp_lines(lines, 3, mode="head")
    assert result.mode == "head"
    assert len(result) == 3


def test_clamp_lines_tail_mode():
    lines = make_lines(8)
    result = clamp_lines(lines, 3, mode="tail")
    assert result.mode == "tail"
    assert result.lines[-1].line_number == 8


def test_clamp_lines_invalid_mode():
    with pytest.raises(ValueError, match="Unknown mode"):
        clamp_lines(make_lines(5), 2, mode="middle")  # type: ignore


def test_clamp_negative_limit():
    with pytest.raises(ValueError, match="limit must be"):
        clamp_head(make_lines(5), -1)


def test_dropped_count():
    lines = make_lines(10)
    result = clamp_head(lines, 4)
    assert result.dropped == 6


def test_format_clamp_contains_summary():
    lines = make_lines(5)
    result = clamp_head(lines, 2)
    output = format_clamp(result)
    assert "# clamped" in output
    assert "head" in output
    assert "limit=2" in output
    assert "dropped=3" in output

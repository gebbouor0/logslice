import pytest
from logslice.parser import LogLine
from logslice.truncator import (
    truncate_message,
    truncate_line,
    truncate_lines,
    format_truncated,
    TruncatedLine,
)


def make_line(raw: str, line_number: int = 1) -> LogLine:
    return LogLine(raw=raw, timestamp=None, level=None, message=raw, line_number=line_number)


def test_truncate_message_no_truncation():
    text = "short"
    result, was = truncate_message(text, 20)
    assert result == text
    assert was is False


def test_truncate_message_exact_length():
    text = "hello"
    result, was = truncate_message(text, 5)
    assert result == text
    assert was is False


def test_truncate_message_truncates():
    result, was = truncate_message("hello world", 8)
    assert result == "hello..."
    assert was is True


def test_truncate_message_custom_ellipsis():
    result, was = truncate_message("abcdefgh", 5, ellipsis="!")
    assert result == "abcd!"
    assert was is True


def test_truncate_message_invalid_max_len():
    with pytest.raises(ValueError):
        truncate_message("text", 0)


def test_truncate_line_not_truncated():
    line = make_line("short line")
    result = truncate_line(line, 50)
    assert result.was_truncated is False
    assert result.display == "short line"
    assert result.original is line


def test_truncate_line_truncated():
    line = make_line("this is a very long log line that exceeds limit")
    result = truncate_line(line, 20)
    assert result.was_truncated is True
    assert len(result.display) == 20
    assert result.display.endswith("...")


def test_truncate_line_preserves_line_number():
    line = make_line("some text", line_number=42)
    result = truncate_line(line, 100)
    assert result.line_number == 42


def test_truncate_line_raw_unchanged():
    raw = "original raw text that is long enough to be truncated easily"
    line = make_line(raw)
    result = truncate_line(line, 10)
    assert result.raw == raw


def test_truncate_lines_count():
    lines = [make_line(f"line {i} with some extra padding text") for i in range(5)]
    results = truncate_lines(lines, 15)
    assert len(results) == 5


def test_truncate_lines_empty():
    assert truncate_lines([], 50) == []


def test_format_truncated_basic():
    lines = [make_line("hello world"), make_line("short")]
    truncated = truncate_lines(lines, 8)
    out = format_truncated(truncated)
    assert len(out) == 2
    assert out[1] == "short"


def test_format_truncated_mark_truncated():
    lines = [make_line("a long line that will be cut"), make_line("tiny")]
    truncated = truncate_lines(lines, 10)
    out = format_truncated(truncated, mark_truncated=True)
    assert "[truncated]" in out[0]
    assert "[truncated]" not in out[1]

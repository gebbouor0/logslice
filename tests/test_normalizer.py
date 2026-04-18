import pytest
from logslice.parser import LogLine
from logslice.normalizer import (
    normalize_message,
    normalize_line,
    normalize_lines,
    NormalizedLine,
)


def make_line(message: str, line_number: int = 1) -> LogLine:
    return LogLine(raw=message, timestamp=None, message=message, line_number=line_number)


def test_normalize_message_strip():
    assert normalize_message("  hello  ") == "hello"


def test_normalize_message_collapse_whitespace():
    assert normalize_message("foo   bar\t baz") == "foo bar baz"


def test_normalize_message_lowercase():
    assert normalize_message("Hello World", lowercase=True) == "hello world"


def test_normalize_message_no_lowercase():
    assert normalize_message("Hello World", lowercase=False) == "Hello World"


def test_normalize_message_remove_ansi():
    msg = "\x1b[31mERROR\x1b[0m something"
    assert normalize_message(msg) == "ERROR something"


def test_normalize_message_keep_ansi():
    msg = "\x1b[31mERROR\x1b[0m"
    result = normalize_message(msg, remove_ansi=False)
    assert "\x1b[" in result


def test_normalize_message_no_strip():
    result = normalize_message("  hi  ", strip=False, collapse_whitespace=False)
    assert result == "  hi  "


def test_normalize_line_returns_normalized_line():
    line = make_line("  hello   world  ")
    result = normalize_line(line)
    assert isinstance(result, NormalizedLine)
    assert result.normalized_message == "hello world"


def test_normalize_line_preserves_original():
    line = make_line("  hello  ")
    result = normalize_line(line)
    assert result.original is line


def test_normalize_line_raw_passthrough():
    line = make_line("raw text")
    result = normalize_line(line)
    assert result.raw == "raw text"


def test_normalize_line_line_number_passthrough():
    line = make_line("msg", line_number=42)
    result = normalize_line(line)
    assert result.line_number == 42


def test_normalize_lines_count():
    lines = [make_line(f"  msg {i}  ") for i in range(5)]
    results = normalize_lines(lines)
    assert len(results) == 5


def test_normalize_lines_all_stripped():
    lines = [make_line("  spaced  "), make_line("\ttabbed\t")]
    results = normalize_lines(lines)
    assert all(r.normalized_message == r.normalized_message.strip() for r in results)


def test_normalize_lines_empty():
    assert normalize_lines([]) == []

"""Tests for logslice.deduplicator."""
import pytest
from logslice.parser import LogLine
from logslice.deduplicator import (
    deduplicate_lines,
    format_deduplicated,
    deduplicate_and_format,
    DeduplicatedLine,
)


def make_line(message: str, raw: str = None, lineno: int = 1) -> LogLine:
    return LogLine(
        raw=raw or message,
        timestamp=None,
        message=message,
        line_number=lineno,
    )


def test_deduplicate_no_duplicates():
    lines = [make_line("alpha", lineno=1), make_line("beta", lineno=2)]
    result = deduplicate_lines(lines)
    assert len(result) == 2
    assert result[0].count == 1
    assert result[1].count == 1


def test_deduplicate_consecutive_duplicates():
    lines = [make_line("err", lineno=i) for i in range(4)]
    result = deduplicate_lines(lines)
    assert len(result) == 1
    assert result[0].count == 4


def test_deduplicate_non_consecutive_not_merged():
    lines = [
        make_line("a", lineno=1),
        make_line("b", lineno=2),
        make_line("a", lineno=3),
    ]
    result = deduplicate_lines(lines)
    assert len(result) == 3


def test_deduplicate_empty():
    assert deduplicate_lines([]) == []


def test_format_single_no_suffix():
    line = make_line("hello", raw="hello")
    deduped = [DeduplicatedLine(line=line, count=1)]
    out = format_deduplicated(deduped)
    assert out == ["hello"]


def test_format_repeated_appends_count():
    line = make_line("oops", raw="oops")
    deduped = [DeduplicatedLine(line=line, count=5)]
    out = format_deduplicated(deduped)
    assert "[repeated 5x]" in out[0]


def test_deduplicate_and_format_returns_both():
    lines = [make_line("x", lineno=i) for i in range(3)]
    deduped, formatted = deduplicate_and_format(lines)
    assert len(deduped) == 1
    assert len(formatted) == 1
    assert "[repeated 3x]" in formatted[0]


def test_format_strips_trailing_newline():
    line = make_line("msg", raw="msg\n")
    deduped = [DeduplicatedLine(line=line, count=1)]
    out = format_deduplicated(deduped)
    assert not out[0].endswith("\n")

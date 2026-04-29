"""Tests for logslice.seeker."""
from datetime import datetime, timezone
from typing import Optional

from logslice.parser import LogLine
from logslice.seeker import SeekHit, SeekResult, format_seek_result, seek_lines


def make_line(
    msg: str,
    line_number: int = 1,
    timestamp: Optional[datetime] = None,
) -> LogLine:
    return LogLine(
        raw=msg,
        message=msg,
        timestamp=timestamp,
        level=None,
        line_number=line_number,
    )


def is_error(line: LogLine) -> bool:
    return "ERROR" in line.message


# --- seek_lines ---

def test_seek_no_match_returns_empty():
    lines = [make_line("INFO ok", i) for i in range(5)]
    result = seek_lines(lines, is_error, term="ERROR")
    assert len(result) == 0
    assert result.total_input == 5


def test_seek_single_match():
    lines = [make_line("INFO", 1), make_line("ERROR boom", 2), make_line("INFO", 3)]
    result = seek_lines(lines, is_error, term="ERROR")
    assert result.hit_count == 1
    assert result.hits[0].line.message == "ERROR boom"


def test_seek_multiple_matches():
    lines = [make_line("ERROR a", i) for i in range(4)]
    result = seek_lines(lines, is_error)
    assert result.hit_count == 4


def test_seek_empty_input():
    result = seek_lines([], is_error)
    assert result.hit_count == 0
    assert result.total_input == 0


def test_seek_term_stored():
    result = seek_lines([], is_error, term="ERROR")
    assert result.term == "ERROR"


def test_seek_context_before():
    lines = [
        make_line("INFO a", 1),
        make_line("INFO b", 2),
        make_line("ERROR c", 3),
    ]
    result = seek_lines(lines, is_error, before=2)
    assert len(result.hits[0].context_before) == 2
    assert result.hits[0].context_before[0].message == "INFO a"


def test_seek_context_after():
    lines = [
        make_line("ERROR x", 1),
        make_line("INFO y", 2),
        make_line("INFO z", 3),
    ]
    result = seek_lines(lines, is_error, after=2)
    assert len(result.hits[0].context_after) == 2


def test_seek_context_clamped_at_start():
    lines = [make_line("ERROR", 1), make_line("INFO", 2)]
    result = seek_lines(lines, is_error, before=10)
    assert result.hits[0].context_before == []


def test_seek_context_clamped_at_end():
    lines = [make_line("INFO", 1), make_line("ERROR", 2)]
    result = seek_lines(lines, is_error, after=10)
    assert result.hits[0].context_after == []


def test_seek_len_equals_hit_count():
    lines = [make_line("ERROR", i) for i in range(3)]
    result = seek_lines(lines, is_error)
    assert len(result) == result.hit_count == 3


# --- format_seek_result ---

def test_format_empty_result():
    result = SeekResult(hits=[], total_input=0, term="")
    assert format_seek_result(result) == []


def test_format_hit_line_prefixed():
    line = make_line("ERROR boom", 5)
    hit = SeekHit(line=line)
    result = SeekResult(hits=[hit], total_input=5, term="ERROR")
    out = format_seek_result(result)
    assert any(">>" in l for l in out)
    assert any("ERROR boom" in l for l in out)


def test_format_context_lines_indented():
    lines = [
        make_line("INFO before", 1),
        make_line("ERROR hit", 2),
        make_line("INFO after", 3),
    ]
    result = seek_lines(lines, is_error, before=1, after=1)
    out = format_seek_result(result)
    before_lines = [l for l in out if "INFO before" in l]
    assert before_lines and before_lines[0].startswith("  ")

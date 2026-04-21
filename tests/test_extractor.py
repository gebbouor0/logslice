"""tests for logslice.extractor"""
from typing import Optional
from datetime import datetime, timezone

import pytest

from logslice.parser import LogLine
from logslice.extractor import extract_fields, format_extracted, ExtractResult


def make_line(
    msg: str,
    line_number: int = 1,
    ts: Optional[datetime] = None,
) -> LogLine:
    return LogLine(
        raw=msg,
        message=msg,
        timestamp=ts,
        level=None,
        line_number=line_number,
    )


PATTERN = r"user=(?P<user>\w+)\s+action=(?P<action>\w+)"


def test_extract_basic_match():
    lines = [make_line("user=alice action=login", 1)]
    result = extract_fields(lines, PATTERN)
    assert len(result) == 1
    assert result.lines[0].fields["user"] == "alice"
    assert result.lines[0].fields["action"] == "login"


def test_extract_no_match_empty_fields():
    lines = [make_line("nothing here", 1)]
    result = extract_fields(lines, PATTERN)
    assert result.lines[0].fields == {}


def test_extract_mixed_lines():
    lines = [
        make_line("user=bob action=logout", 1),
        make_line("unrelated log entry", 2),
        make_line("user=carol action=view", 3),
    ]
    result = extract_fields(lines, PATTERN)
    assert len(result.matched) == 2
    assert len(result.unmatched) == 1


def test_extract_empty_input():
    result = extract_fields([], PATTERN)
    assert len(result) == 0
    assert result.matched == []
    assert result.unmatched == []


def test_extract_column_returns_values():
    lines = [
        make_line("user=dave action=delete", 1),
        make_line("no match", 2),
        make_line("user=eve action=create", 3),
    ]
    result = extract_fields(lines, PATTERN)
    users = result.column("user")
    assert users[0] == "dave"
    assert users[1] is None
    assert users[2] == "eve"


def test_extract_case_insensitive_default():
    lines = [make_line("USER=frank ACTION=read", 1)]
    result = extract_fields(lines, PATTERN)
    assert result.lines[0].fields.get("user") == "frank"


def test_extract_preserves_line_number():
    lines = [make_line("user=x action=y", 42)]
    result = extract_fields(lines, PATTERN)
    assert result.lines[0].line_number == 42


def test_extract_preserves_raw():
    raw = "user=g action=h"
    lines = [make_line(raw, 1)]
    result = extract_fields(lines, PATTERN)
    assert result.lines[0].raw == raw


def test_format_extracted_match_shows_fields():
    lines = [make_line("user=h action=jump", 1)]
    result = extract_fields(lines, PATTERN)
    output = format_extracted(result)
    assert "user=h" in output
    assert "action=jump" in output


def test_format_extracted_no_match_shows_placeholder():
    lines = [make_line("nothing", 5)]
    result = extract_fields(lines, PATTERN)
    output = format_extracted(result)
    assert "<no match>" in output
    assert "[5]" in output


def test_format_extracted_empty():
    result = ExtractResult(pattern=PATTERN)
    output = format_extracted(result)
    assert output == ""

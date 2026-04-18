"""Tests for logslice.annotator."""
import pytest
from datetime import datetime
from logslice.parser import LogLine
from logslice.annotator import (
    AnnotatedLine,
    annotate_lines,
    format_annotated,
)


def make_line(raw: str, n: int = 1) -> LogLine:
    return LogLine(raw=raw, timestamp=None, line_number=n)


def test_annotate_no_rules_no_tags():
    lines = [make_line("INFO server started")]
    result = annotate_lines(lines, {})
    assert result[0].tags == []
    assert result[0].note is None


def test_annotate_single_rule_matches():
    lines = [make_line("ERROR disk full"), make_line("INFO all good", 2)]
    result = annotate_lines(lines, {"error": "ERROR"})
    assert result[0].tags == ["error"]
    assert result[1].tags == []


def test_annotate_multiple_rules():
    lines = [make_line("WARN ERROR both present")]
    result = annotate_lines(lines, {"warn": "WARN", "error": "ERROR"})
    assert set(result[0].tags) == {"warn", "error"}


def test_annotate_note_pattern_match():
    lines = [make_line("CRITICAL system failure")]
    result = annotate_lines(lines, {}, note_pattern=r"CRITICAL")
    assert result[0].note is not None
    assert "CRITICAL" in result[0].note


def test_annotate_note_pattern_no_match():
    lines = [make_line("INFO heartbeat")]
    result = annotate_lines(lines, {}, note_pattern=r"CRITICAL")
    assert result[0].note is None


def test_annotate_preserves_line_number():
    lines = [make_line("DEBUG foo", n=42)]
    result = annotate_lines(lines, {})
    assert result[0].line_number == 42


def test_format_annotated_with_tags():
    lines = [make_line("ERROR boom")]
    annotated = annotate_lines(lines, {"error": "ERROR"})
    out = format_annotated(annotated)
    assert out[0].startswith("[error]")
    assert "ERROR boom" in out[0]


def test_format_annotated_no_tags_shown():
    lines = [make_line("ERROR boom")]
    annotated = annotate_lines(lines, {"error": "ERROR"})
    out = format_annotated(annotated, show_tags=False)
    assert not out[0].startswith("[")


def test_format_annotated_note_appended():
    lines = [make_line("CRITICAL meltdown")]
    annotated = annotate_lines(lines, {}, note_pattern=r"CRITICAL")
    out = format_annotated(annotated)
    assert "#" in out[0]


def test_format_annotated_empty():
    assert format_annotated([]) == []

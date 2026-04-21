"""Tests for logslice.inspector."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

import pytest

from logslice.parser import LogLine
from logslice.inspector import (
    InspectionResult,
    format_inspection,
    inspect_lines,
)


def make_line(
    message: str,
    line_number: int = 1,
    timestamp: Optional[datetime] = None,
) -> LogLine:
    return LogLine(
        raw=message,
        message=message,
        timestamp=timestamp,
        line_number=line_number,
    )


def dt() -> datetime:
    return datetime(2024, 6, 1, 12, 0, 0)


# --- basic counts ---

def test_inspect_total_lines():
    lines = [make_line("hello", 1), make_line("world", 2)]
    result = inspect_lines(lines)
    assert result.total_lines == 2


def test_inspect_empty_input():
    result = inspect_lines([])
    assert result.total_lines == 0
    assert result.timestamp_coverage == 0.0


def test_inspect_timestamp_coverage_full():
    lines = [make_line("a", 1, dt()), make_line("b", 2, dt())]
    result = inspect_lines(lines)
    assert result.timestamp_coverage == 1.0


def test_inspect_timestamp_coverage_partial():
    lines = [make_line("a", 1, dt()), make_line("b", 2, None)]
    result = inspect_lines(lines)
    assert result.timestamp_coverage == 0.5


def test_inspect_lines_without_timestamp():
    lines = [make_line("a"), make_line("b"), make_line("c", timestamp=dt())]
    result = inspect_lines(lines)
    assert result.lines_without_timestamp == 2
    assert result.lines_with_timestamp == 1


# --- level detection ---

def test_inspect_level_counts_error():
    lines = [make_line("ERROR something broke"), make_line("all good")]
    result = inspect_lines(lines)
    assert result.level_counts.get("error", 0) == 1


def test_inspect_level_counts_warning():
    lines = [make_line("WARN disk full")]
    result = inspect_lines(lines)
    assert result.level_counts.get("warning", 0) == 1


def test_inspect_level_unknown():
    lines = [make_line("just some text")]
    result = inspect_lines(lines)
    assert result.level_counts.get("unknown", 0) == 1


# --- duplicates ---

def test_inspect_no_duplicates():
    lines = [make_line("a"), make_line("b"), make_line("c")]
    result = inspect_lines(lines)
    assert result.duplicate_count == 0


def test_inspect_duplicate_count():
    lines = [make_line("same"), make_line("same"), make_line("same")]
    result = inspect_lines(lines)
    assert result.duplicate_count == 2


# --- empty messages ---

def test_inspect_empty_message_count():
    lines = [make_line(""), make_line("  "), make_line("real")]
    result = inspect_lines(lines)
    assert result.empty_message_count == 2


# --- issues ---

def test_inspect_issues_missing_timestamps():
    lines = [make_line("a")]
    result = inspect_lines(lines)
    assert any("missing timestamps" in i for i in result.issues)


def test_inspect_no_issues_when_clean():
    lines = [make_line("info all good", timestamp=dt())]
    result = inspect_lines(lines)
    assert not any("missing" in i for i in result.issues)
    assert not any("duplicate" in i for i in result.issues)
    assert not any("empty" in i for i in result.issues)


# --- format ---

def test_format_inspection_contains_header():
    result = inspect_lines([make_line("hello", timestamp=dt())])
    text = format_inspection(result)
    assert "Inspection report" in text


def test_format_inspection_shows_coverage():
    result = inspect_lines([make_line("x", timestamp=dt())])
    text = format_inspection(result)
    assert "100.0%" in text


def test_format_inspection_no_issues_message():
    result = inspect_lines([make_line("info ok", timestamp=dt())])
    text = format_inspection(result)
    assert "No issues found" in text

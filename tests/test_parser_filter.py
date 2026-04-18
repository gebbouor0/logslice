"""Tests for log parsing and filtering."""

from datetime import datetime

import pytest

from logslice.filter import filter_lines, format_output
from logslice.parser import parse_line, parse_lines, parse_timestamp


SAMPLE_LINES = [
    "2024-01-15T08:00:00 INFO  service started\n",
    "2024-01-15T08:05:30 DEBUG connection established\n",
    "2024-01-15T09:10:00 ERROR failed to connect to db\n",
    "no timestamp here, just noise\n",
    "2024-01-15T10:00:00 INFO  shutdown complete\n",
]


def test_parse_timestamp_iso():
    ts = parse_timestamp("2024-01-15T08:00:00 INFO something")
    assert ts == datetime(2024, 1, 15, 8, 0, 0)


def test_parse_timestamp_none():
    assert parse_timestamp("no timestamp here") is None


def test_parse_line_sets_line_number():
    line = parse_line("2024-01-15T08:00:00 INFO hello\n", 42)
    assert line.line_number == 42
    assert line.raw == "2024-01-15T08:00:00 INFO hello"


def test_parse_lines_count():
    parsed = parse_lines(SAMPLE_LINES)
    assert len(parsed) == 5


def test_filter_by_start():
    lines = parse_lines(SAMPLE_LINES)
    result = filter_lines(lines, start=datetime(2024, 1, 15, 9, 0, 0))
    assert len(result) == 2
    assert "ERROR" in result[0].raw


def test_filter_by_time_range():
    lines = parse_lines(SAMPLE_LINES)
    result = filter_lines(
        lines,
        start=datetime(2024, 1, 15, 8, 0, 0),
        end=datetime(2024, 1, 15, 9, 0, 0),
    )
    assert len(result) == 2


def test_filter_excludes_no_timestamp_when_time_active():
    lines = parse_lines(SAMPLE_LINES)
    result = filter_lines(lines, start=datetime(2024, 1, 15, 0, 0, 0))
    assert all(l.timestamp is not None for l in result)


def test_filter_by_pattern():
    lines = parse_lines(SAMPLE_LINES)
    result = filter_lines(lines, pattern=r"ERROR|WARN")
    assert len(result) == 1
    assert "ERROR" in result[0].raw


def test_filter_no_criteria_returns_all():
    lines = parse_lines(SAMPLE_LINES)
    result = filter_lines(lines)
    assert len(result) == 5


def test_format_output_with_line_numbers():
    lines = parse_lines(["2024-01-15T08:00:00 INFO hello\n"])
    out = format_output(lines, show_line_numbers=True)
    assert "1:" in out
    assert "INFO hello" in out

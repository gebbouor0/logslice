"""Tests for logslice.scanner."""
import pytest
from logslice.parser import LogLine
from logslice.scanner import ScanMatch, ScanResult, scan_lines, format_scan


def make_line(msg: str, lineno: int = 1) -> LogLine:
    return LogLine(raw=msg, message=msg, timestamp=None, line_number=lineno)


# --- scan_lines ---

def test_scan_basic_match():
    lines = [make_line("ERROR: disk full", 1), make_line("INFO: all ok", 2)]
    result = scan_lines(lines, r"error")
    assert result.total_matches == 1
    assert result.matches[0].line.line_number == 1


def test_scan_no_match():
    lines = [make_line("INFO: all ok", 1)]
    result = scan_lines(lines, r"error")
    assert result.total_matches == 0
    assert result.total_input == 1


def test_scan_empty_input():
    result = scan_lines([], r"error")
    assert result.total_matches == 0
    assert result.total_input == 0
    assert result.hit_rate == 0.0


def test_scan_case_sensitive_no_match():
    lines = [make_line("ERROR: disk full", 1)]
    result = scan_lines(lines, r"error", case_sensitive=True)
    assert result.total_matches == 0


def test_scan_case_sensitive_match():
    lines = [make_line("ERROR: disk full", 1)]
    result = scan_lines(lines, r"ERROR", case_sensitive=True)
    assert result.total_matches == 1


def test_scan_multiple_spans():
    lines = [make_line("foo foo foo", 1)]
    result = scan_lines(lines, r"foo")
    assert result.matches[0].match_count == 3
    assert len(result.matches[0].spans) == 3


def test_scan_hit_rate():
    lines = [make_line("ERROR", 1), make_line("INFO", 2), make_line("ERROR", 3)]
    result = scan_lines(lines, r"error")
    assert result.hit_rate == pytest.approx(2 / 3)


def test_scan_invalid_pattern_raises():
    with pytest.raises(ValueError, match="Invalid pattern"):
        scan_lines([make_line("hello")], r"[invalid")


def test_scan_match_raw_and_line_number():
    line = make_line("WARN: low memory", 7)
    result = scan_lines([line], r"warn")
    m = result.matches[0]
    assert m.raw == "WARN: low memory"
    assert m.line_number == 7


def test_scan_result_pattern_stored():
    result = scan_lines([], r"foo")
    assert result.pattern == r"foo"


# --- format_scan ---

def test_format_scan_header():
    lines = [make_line("ERROR here", 1)]
    result = scan_lines(lines, r"error")
    out = format_scan(result)
    assert any("Pattern" in l for l in out)
    assert any("Matches" in l for l in out)


def test_format_scan_includes_line():
    lines = [make_line("ERROR here", 3)]
    result = scan_lines(lines, r"error")
    out = format_scan(result)
    combined = "\n".join(out)
    assert "ERROR here" in combined
    assert "[3]" in combined


def test_format_scan_empty_no_line_entries():
    result = scan_lines([], r"error")
    out = format_scan(result)
    # Only header lines, nothing after separator
    sep_idx = next(i for i, l in enumerate(out) if l.startswith("-"))
    assert len(out) == sep_idx + 1

import pytest
from logslice.parser import LogLine
from logslice.labeler import (
    LabeledLine,
    label_line,
    label_lines,
    format_labeled,
    group_by_label,
)


def make_line(message: str, line_number: int = 1) -> LogLine:
    return LogLine(raw=message, message=message, timestamp=None, line_number=line_number)


def test_label_line_single_match():
    line = make_line("ERROR: disk full")
    result = label_line(line, {"error": r"ERROR"})
    assert "error" in result.labels


def test_label_line_no_match():
    line = make_line("INFO: all good")
    result = label_line(line, {"error": r"ERROR"})
    assert result.labels == {}


def test_label_line_multiple_rules():
    line = make_line("ERROR: disk full WARNING")
    result = label_line(line, {"error": r"ERROR", "warning": r"WARNING"})
    assert "error" in result.labels
    assert "warning" in result.labels


def test_label_line_preserves_raw():
    line = make_line("some message")
    result = label_line(line, {})
    assert result.raw == "some message"


def test_label_line_preserves_line_number():
    line = make_line("msg", line_number=42)
    result = label_line(line, {})
    assert result.line_number == 42


def test_label_lines_count():
    lines = [make_line(f"line {i}") for i in range(5)]
    result = label_lines(lines, {"has_line": r"line"})
    assert len(result) == 5
    assert all("has_line" in r.labels for r in result)


def test_label_lines_empty():
    result = label_lines([], {"k": r"v"})
    assert result == []


def test_format_labeled_with_labels():
    line = make_line("ERROR: boom")
    labeled = label_line(line, {"error": r"ERROR"})
    out = format_labeled(labeled)
    assert "error" in out
    assert "ERROR: boom" in out


def test_format_labeled_no_labels():
    line = make_line("INFO: ok")
    labeled = label_line(line, {})
    out = format_labeled(labeled)
    assert "(none)" in out


def test_format_labeled_custom_separator():
    line = make_line("WARN: low disk")
    labeled = label_line(line, {"warn": r"WARN"})
    out = format_labeled(labeled, separator=" >> ")
    assert " >> " in out


def test_group_by_label_basic():
    lines = [
        make_line("ERROR: x"),
        make_line("INFO: y"),
        make_line("ERROR: z"),
    ]
    labeled = label_lines(lines, {"error": r"ERROR"})
    groups = group_by_label(labeled)
    assert len(groups["error"]) == 2
    assert len(groups["unlabeled"]) == 1


def test_group_by_label_empty():
    groups = group_by_label([])
    assert groups == {}

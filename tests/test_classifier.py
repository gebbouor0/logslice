import pytest
from datetime import datetime
from logslice.parser import LogLine
from logslice.classifier import ClassifiedLine, ClassifyResult, classify_lines


def make_line(msg: str, n: int = 1) -> LogLine:
    return LogLine(
        raw=msg,
        timestamp=datetime(2024, 1, 1, 12, 0, 0),
        message=msg,
        line_number=n,
    )


def test_classify_single_rule_match():
    lines = [make_line("ERROR: disk full", 1)]
    result = classify_lines(lines, {"errors": r"error"})
    assert "errors" in result.categories
    assert len(result.categories["errors"]) == 1


def test_classify_default_category():
    lines = [make_line("INFO: all good", 1)]
    result = classify_lines(lines, {"errors": r"error"})
    assert "uncategorized" in result.categories
    assert result.categories["uncategorized"][0].matched_rule is None


def test_classify_custom_default_category():
    lines = [make_line("DEBUG: verbose", 1)]
    result = classify_lines(lines, {"errors": r"error"}, default_category="other")
    assert "other" in result.categories


def test_classify_multiple_rules_first_wins():
    lines = [make_line("ERROR warning combo", 1)]
    rules = {"errors": r"error", "warnings": r"warning"}
    result = classify_lines(lines, rules)
    assert "errors" in result.categories
    assert "warnings" not in result.categories


def test_classify_case_insensitive_default():
    lines = [make_line("error: something", 1)]
    result = classify_lines(lines, {"errors": r"ERROR"})
    assert "errors" in result.categories


def test_classify_case_sensitive():
    lines = [make_line("error: something", 1)]
    result = classify_lines(lines, {"errors": r"ERROR"}, case_sensitive=True)
    assert "errors" not in result.categories
    assert "uncategorized" in result.categories


def test_classify_empty_lines():
    result = classify_lines([], {"errors": r"error"})
    assert result.categories == {}


def test_classify_all_lines_sorted():
    lines = [make_line("INFO ok", 3), make_line("ERROR bad", 1), make_line("WARN meh", 2)]
    rules = {"errors": r"error", "warnings": r"warn"}
    result = classify_lines(lines, rules)
    all_lines = result.all_lines()
    numbers = [l.line_number for l in all_lines]
    assert numbers == sorted(numbers)


def test_classified_line_properties():
    line = make_line("ERROR: oops", 5)
    cl = ClassifiedLine(log_line=line, category="errors", matched_rule="errors")
    assert cl.raw == "ERROR: oops"
    assert cl.line_number == 5

"""Tests for logslice.weigher."""
import pytest
from logslice.parser import LogLine
from logslice.weigher import (
    WeightRule,
    WeighResult,
    WeightedLine,
    weigh_lines,
    format_weighed,
)


def make_line(msg: str, number: int = 1) -> LogLine:
    return LogLine(raw=msg, message=msg, timestamp=None, level=None, line_number=number)


def is_error(line: LogLine) -> bool:
    return "error" in line.message.lower()


def is_warn(line: LogLine) -> bool:
    return "warn" in line.message.lower()


def test_weigh_default_weight_no_rules():
    lines = [make_line("hello", 1), make_line("world", 2)]
    result = weigh_lines(lines, rules=[], default_weight=1.0)
    assert len(result) == 2
    assert all(wl.weight == 1.0 for wl in result.lines)


def test_weigh_single_rule_match():
    rules = [WeightRule(predicate=is_error, weight=5.0, label="error")]
    lines = [make_line("an error occurred", 1), make_line("all good", 2)]
    result = weigh_lines(lines, rules)
    assert result.lines[0].weight == 5.0
    assert result.lines[1].weight == 0.0


def test_weigh_multiple_rules_sum():
    rules = [
        WeightRule(predicate=is_error, weight=5.0),
        WeightRule(predicate=is_warn, weight=2.0),
    ]
    lines = [make_line("error warn combo", 1)]
    result = weigh_lines(lines, rules)
    assert result.lines[0].weight == 7.0


def test_weigh_empty_input():
    result = weigh_lines([], rules=[])
    assert len(result) == 0


def test_weigh_top_returns_highest():
    rules = [WeightRule(predicate=is_error, weight=10.0)]
    lines = [make_line("ok", 1), make_line("error", 2), make_line("fine", 3)]
    result = weigh_lines(lines, rules)
    top = result.top(1)
    assert len(top) == 1
    assert top[0].weight == 10.0
    assert top[0].line_number == 2


def test_weigh_bottom_returns_lowest():
    rules = [WeightRule(predicate=is_error, weight=10.0)]
    lines = [make_line("error", 1), make_line("ok", 2)]
    result = weigh_lines(lines, rules)
    bottom = result.bottom(1)
    assert bottom[0].weight == 0.0


def test_weigh_above_threshold():
    rules = [WeightRule(predicate=is_error, weight=8.0)]
    lines = [make_line("error here", 1), make_line("nothing", 2), make_line("error again", 3)]
    result = weigh_lines(lines, rules)
    above = result.above(5.0)
    assert len(above) == 2


def test_weigh_negative_weight():
    rules = [WeightRule(predicate=is_warn, weight=-3.0)]
    lines = [make_line("just a warning", 1)]
    result = weigh_lines(lines, rules, default_weight=1.0)
    assert result.lines[0].weight == -2.0


def test_format_weighed_basic():
    rules = [WeightRule(predicate=is_error, weight=5.0)]
    lines = [make_line("error found", 1), make_line("ok", 2)]
    result = weigh_lines(lines, rules)
    formatted = format_weighed(result)
    assert len(formatted) == 2
    assert "[+5.0]" in formatted[0]
    assert "#1" in formatted[0]


def test_format_weighed_top_n():
    rules = [WeightRule(predicate=is_error, weight=9.0)]
    lines = [make_line("error", 1), make_line("ok", 2), make_line("fine", 3)]
    result = weigh_lines(lines, rules)
    formatted = format_weighed(result, top_n=1)
    assert len(formatted) == 1
    assert "[+9.0]" in formatted[0]


def test_weighted_line_properties():
    line = make_line("test message", 42)
    wl = WeightedLine(_line=line, weight=3.5)
    assert wl.raw == "test message"
    assert wl.line_number == 42
    assert wl.message == "test message"
    assert wl.weight == 3.5

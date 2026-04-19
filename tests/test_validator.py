import pytest
from datetime import datetime
from logslice.parser import LogLine
from logslice.validator import (
    ValidationRule, validate_lines, format_violations,
    HAS_TIMESTAMP, HAS_LEVEL, NON_EMPTY_MESSAGE,
)


def make_line(msg="hello", level="INFO", ts=None, lineno=1):
    return LogLine(raw=msg, message=msg, timestamp=ts, level=level, line_number=lineno)


TS = datetime(2024, 1, 1, 12, 0, 0)


def test_validate_clean():
    lines = [make_line(ts=TS)]
    result = validate_lines(lines, [HAS_TIMESTAMP])
    assert result.is_clean
    assert result.valid_count == 1


def test_validate_missing_timestamp():
    lines = [make_line(ts=None)]
    result = validate_lines(lines, [HAS_TIMESTAMP])
    assert not result.is_clean
    assert len(result.violations) == 1
    assert result.violations[0].rule_name == "has_timestamp"


def test_validate_missing_level():
    lines = [make_line(level="")]
    result = validate_lines(lines, [HAS_LEVEL])
    assert len(result.violations) == 1


def test_validate_empty_message():
    lines = [make_line(msg="   ")]
    result = validate_lines(lines, [NON_EMPTY_MESSAGE])
    assert len(result.violations) == 1


def test_validate_multiple_rules_multiple_violations():
    lines = [make_line(msg="", level="", ts=None)]
    result = validate_lines(lines, [HAS_TIMESTAMP, HAS_LEVEL, NON_EMPTY_MESSAGE])
    assert len(result.violations) == 3


def test_validate_empty_input():
    result = validate_lines([], [HAS_TIMESTAMP])
    assert result.is_clean
    assert result.total == 0


def test_format_violations_clean():
    lines = [make_line(ts=TS)]
    result = validate_lines(lines, [HAS_TIMESTAMP])
    out = format_violations(result)
    assert "passed" in out


def test_format_violations_shows_line_number():
    lines = [make_line(ts=None, lineno=42)]
    result = validate_lines(lines, [HAS_TIMESTAMP])
    out = format_violations(result)
    assert "42" in out
    assert "has_timestamp" in out


def test_custom_rule():
    rule = ValidationRule(
        name="no_debug",
        check=lambda l: l.level != "DEBUG",
        message="debug lines not allowed",
    )
    lines = [make_line(level="DEBUG"), make_line(level="INFO")]
    result = validate_lines(lines, [rule])
    assert len(result.violations) == 1
    assert result.valid_count == 1

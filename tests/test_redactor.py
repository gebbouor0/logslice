"""Tests for logslice.redactor."""
import pytest
from datetime import datetime
from logslice.parser import LogLine
from logslice.redactor import (
    redact_message,
    redact_line,
    redact_lines,
    BUILTIN_PATTERNS,
    DEFAULT_PLACEHOLDER,
)


def make_line(message: str, line_number: int = 1) -> LogLine:
    return LogLine(
        raw=message,
        timestamp=datetime(2024, 1, 1, 12, 0, 0),
        message=message,
        line_number=line_number,
    )


def test_redact_message_basic():
    result, matched = redact_message("user email is foo@example.com", [BUILTIN_PATTERNS["email"]])
    assert "[REDACTED]" in result
    assert "foo@example.com" not in result
    assert len(matched) == 1


def test_redact_message_no_match():
    result, matched = redact_message("nothing sensitive here", [BUILTIN_PATTERNS["email"]])
    assert result == "nothing sensitive here"
    assert matched == []


def test_redact_message_custom_placeholder():
    result, _ = redact_message("ip 192.168.1.1 seen", [BUILTIN_PATTERNS["ip"]], placeholder="***")
    assert "***" in result
    assert "192.168.1.1" not in result


def test_redact_message_multiple_patterns():
    msg = "email foo@bar.com ip 10.0.0.1"
    patterns = [BUILTIN_PATTERNS["email"], BUILTIN_PATTERNS["ip"]]
    result, matched = redact_message(msg, patterns)
    assert "foo@bar.com" not in result
    assert "10.0.0.1" not in result
    assert len(matched) == 2


def test_redact_line_preserves_original():
    line = make_line("token=abc123 in log")
    redacted = redact_line(line, [BUILTIN_PATTERNS["token"]])
    assert redacted.original is line
    assert redacted.line_number == 1
    assert "[REDACTED]" in redacted.redacted_message


def test_redact_line_no_match():
    line = make_line("clean log line")
    redacted = redact_line(line, [BUILTIN_PATTERNS["email"]])
    assert redacted.redacted_message == "clean log line"
    assert redacted.matched_patterns == []


def test_redact_lines_count():
    lines = [make_line(f"user{i}@example.com logged in", i) for i in range(5)]
    results = redact_lines(lines, [], builtins=["email"])
    assert len(results) == 5
    assert all("[REDACTED]" in r.redacted_message for r in results)


def test_redact_lines_builtins_unknown_ignored():
    lines = [make_line("some log")]
    results = redact_lines(lines, [], builtins=["nonexistent"])
    assert results[0].redacted_message == "some log"


def test_redact_lines_uuid_builtin():
    uuid = "123e4567-e89b-12d3-a456-426614174000"
    lines = [make_line(f"request id {uuid}")]
    results = redact_lines(lines, [], builtins=["uuid"])
    assert uuid not in results[0].redacted_message
    assert "[REDACTED]" in results[0].redacted_message

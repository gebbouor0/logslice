"""Tests for logslice.masker."""
import pytest
from datetime import datetime
from logslice.parser import LogLine
from logslice.masker import (
    BUILTIN_PATTERNS,
    MaskedLine,
    mask_message,
    mask_line,
    mask_lines,
)


def make_line(message: str, line_number: int = 1, ts: datetime | None = None) -> LogLine:
    return LogLine(
        raw=message,
        timestamp=ts,
        level=None,
        message=message,
        line_number=line_number,
    )


# --- mask_message ---

def test_mask_message_ip():
    text = "request from 192.168.1.1 failed"
    result, applied = mask_message(text, {"ip": BUILTIN_PATTERNS["ip"]})
    assert "192.168.1.1" not in result
    assert "[MASKED]" in result
    assert "ip" in applied


def test_mask_message_email():
    text = "user admin@example.com logged in"
    result, applied = mask_message(text, {"email": BUILTIN_PATTERNS["email"]})
    assert "admin@example.com" not in result
    assert "email" in applied


def test_mask_message_no_match_returns_original():
    text = "nothing sensitive here"
    result, applied = mask_message(text, {"ip": BUILTIN_PATTERNS["ip"]})
    assert result == text
    assert applied == []


def test_mask_message_custom_placeholder():
    text = "token=abc123"
    result, applied = mask_message(text, {"token": BUILTIN_PATTERNS["token"]}, placeholder="***")
    assert "***" in result
    assert "abc123" not in result


def test_mask_message_multiple_patterns():
    text = "user foo@bar.com from 10.0.0.1"
    result, applied = mask_message(
        text,
        {"email": BUILTIN_PATTERNS["email"], "ip": BUILTIN_PATTERNS["ip"]},
    )
    assert "foo@bar.com" not in result
    assert "10.0.0.1" not in result
    assert set(applied) == {"email", "ip"}


# --- mask_line ---

def test_mask_line_returns_masked_line():
    line = make_line("connect from 172.16.0.5")
    result = mask_line(line, {"ip": BUILTIN_PATTERNS["ip"]})
    assert isinstance(result, MaskedLine)
    assert "172.16.0.5" not in result.masked_message
    assert result.raw == line.raw
    assert result.line_number == 1


def test_mask_line_no_message():
    line = LogLine(raw="bare", timestamp=None, level=None, message=None, line_number=2)
    result = mask_line(line, {"ip": BUILTIN_PATTERNS["ip"]})
    assert result.masked_message == ""
    assert result.applied_masks == []


# --- mask_lines ---

def test_mask_lines_uses_builtins_by_default():
    lines = [
        make_line("ip 1.2.3.4 seen", 1),
        make_line("no match here", 2),
    ]
    results = mask_lines(lines)
    assert "1.2.3.4" not in results[0].masked_message
    assert results[1].masked_message == "no match here"


def test_mask_lines_disable_builtins():
    lines = [make_line("ip 1.2.3.4 seen", 1)]
    results = mask_lines(lines, use_builtins=False)
    # no patterns applied, message unchanged
    assert "1.2.3.4" in results[0].masked_message


def test_mask_lines_extra_patterns():
    lines = [make_line("order=XYZ999 placed", 1)]
    results = mask_lines(
        lines,
        use_builtins=False,
        extra_patterns={"order": r"order=[A-Z0-9]+"},
    )
    assert "XYZ999" not in results[0].masked_message
    assert "order" in results[0].applied_masks


def test_mask_lines_empty_input():
    assert mask_lines([]) == []

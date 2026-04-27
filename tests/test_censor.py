"""Tests for logslice/censor.py."""
import pytest
from logslice.parser import LogLine
from logslice.censor import (
    censor_lines,
    format_censor,
    CensorResult,
    CensoredLine,
)


def make_line(msg: str, n: int = 1) -> LogLine:
    ll = LogLine(raw=msg, line_number=n)
    ll.message = msg
    ll.timestamp = None
    ll.level = None
    return ll


def test_censor_ip_basic():
    lines = [make_line("connected from 192.168.1.1 ok")]
    result = censor_lines(lines, categories=["ip"])
    assert result.total_censored == 1
    assert "192.168.1.1" not in result.lines[0].message
    assert "[CENSORED]" in result.lines[0].message


def test_censor_email_basic():
    lines = [make_line("user admin@example.com logged in")]
    result = censor_lines(lines, categories=["email"])
    assert result.total_censored == 1
    assert "admin@example.com" not in result.lines[0].message


def test_censor_no_match_not_flagged():
    lines = [make_line("nothing sensitive here")]
    result = censor_lines(lines, categories=["ip", "email"])
    assert result.total_censored == 0
    assert result.lines[0].was_censored is False
    assert result.lines[0].message == "nothing sensitive here"


def test_censor_empty_input():
    result = censor_lines([], categories=["ip"])
    assert result.total_input == 0
    assert result.total_censored == 0
    assert len(result) == 0


def test_censor_rate_zero_when_no_input():
    result = CensorResult()
    assert result.censor_rate == 0.0


def test_censor_rate_calculation():
    lines = [
        make_line("ip 10.0.0.1 here", 1),
        make_line("nothing", 2),
        make_line("ip 10.0.0.2 here", 3),
    ]
    result = censor_lines(lines, categories=["ip"])
    assert result.censor_rate == pytest.approx(2 / 3)


def test_censor_categories_hit_recorded():
    lines = [make_line("ip 1.2.3.4 email foo@bar.com")]
    result = censor_lines(lines, categories=["ip", "email"])
    assert "ip" in result.lines[0].categories_hit
    assert "email" in result.lines[0].categories_hit


def test_censor_custom_placeholder():
    lines = [make_line("addr 10.0.0.1")]
    result = censor_lines(lines, categories=["ip"], placeholder="***")
    assert "***" in result.lines[0].message


def test_censor_extra_patterns():
    lines = [make_line("secret=abc123")]
    result = censor_lines(
        lines,
        categories=[],
        extra_patterns={"secret": r"secret=\S+"},
    )
    assert result.total_censored == 1
    assert "secret" in result.lines[0].categories_hit


def test_censor_uuid():
    lines = [make_line("id=550e8400-e29b-41d4-a716-446655440000 done")]
    result = censor_lines(lines, categories=["uuid"])
    assert result.total_censored == 1


def test_censor_preserves_line_number():
    lines = [make_line("x", n=42)]
    result = censor_lines(lines, categories=["ip"])
    assert result.lines[0].line_number == 42


def test_format_censor_marks_censored_lines():
    lines = [
        make_line("ip 1.2.3.4", 1),
        make_line("clean", 2),
    ]
    result = censor_lines(lines, categories=["ip"])
    out = format_censor(result)
    assert "[*]" in out[0]
    assert "[*]" not in out[1]


def test_censor_all_categories_by_default():
    lines = [make_line("ip 1.2.3.4 email a@b.com")]
    # no categories kwarg — should use all builtins
    result = censor_lines(lines)
    assert result.total_censored == 1


def test_censor_as_log_line_roundtrip():
    lines = [make_line("hello world", 7)]
    result = censor_lines(lines, categories=[])
    ll = result.lines[0].as_log_line()
    assert ll.line_number == 7
    assert ll.message == "hello world"

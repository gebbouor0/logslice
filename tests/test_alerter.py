import pytest
from logslice.parser import LogLine
from logslice.alerter import AlertRule, check_alerts, format_alerts
from datetime import datetime


def make_line(msg: str, n: int = 1) -> LogLine:
    return LogLine(
        raw=msg,
        message=msg,
        timestamp=datetime(2024, 1, 1, 12, 0, 0),
        line_number=n,
    )


def test_check_alerts_basic_match():
    lines = [make_line("ERROR: disk full", 1)]
    rules = [AlertRule(name="disk", pattern="disk full", threshold=1)]
    result = check_alerts(lines, rules)
    assert len(result.alerts) == 1
    assert result.alerts[0].triggered


def test_check_alerts_below_threshold():
    lines = [make_line("ERROR: disk full", 1)]
    rules = [AlertRule(name="disk", pattern="disk full", threshold=3)]
    result = check_alerts(lines, rules)
    assert not result.alerts[0].triggered
    assert result.triggered == []


def test_check_alerts_multiple_matches():
    lines = [
        make_line("ERROR: timeout", 1),
        make_line("ERROR: timeout", 2),
        make_line("INFO: ok", 3),
    ]
    rules = [AlertRule(name="timeout", pattern="timeout", threshold=2)]
    result = check_alerts(lines, rules)
    assert result.alerts[0].count == 2
    assert result.alerts[0].triggered


def test_check_alerts_no_match():
    lines = [make_line("INFO: all good", 1)]
    rules = [AlertRule(name="error", pattern="ERROR", threshold=1)]
    result = check_alerts(lines, rules)
    assert result.alerts[0].count == 0
    assert not result.alerts[0].triggered


def test_check_alerts_case_insensitive():
    lines = [make_line("error: something", 1)]
    rules = [AlertRule(name="err", pattern="ERROR", threshold=1)]
    result = check_alerts(lines, rules)
    assert result.alerts[0].triggered


def test_check_alerts_multiple_rules():
    lines = [make_line("CRITICAL failure", 1), make_line("WARN low memory", 2)]
    rules = [
        AlertRule(name="crit", pattern="critical", threshold=1),
        AlertRule(name="warn", pattern="warn", threshold=1),
    ]
    result = check_alerts(lines, rules)
    assert len(result.triggered) == 2


def test_format_alerts_triggered():
    lines = [make_line("disk full", 1)]
    rules = [AlertRule(name="disk", pattern="disk", threshold=1, description="Check disk")]
    result = check_alerts(lines, rules)
    output = format_alerts(result)
    assert "[ALERT]" in output
    assert "disk" in output
    assert "Check disk" in output


def test_format_alerts_none_triggered():
    lines = [make_line("all ok", 1)]
    rules = [AlertRule(name="err", pattern="ERROR", threshold=1)]
    result = check_alerts(lines, rules)
    output = format_alerts(result)
    assert output == "No alerts triggered."


def test_check_alerts_empty_lines():
    result = check_alerts([], [AlertRule(name="x", pattern="x", threshold=1)])
    assert result.alerts[0].count == 0


def test_check_alerts_empty_rules():
    lines = [make_line("ERROR", 1)]
    result = check_alerts(lines, [])
    assert result.alerts == []

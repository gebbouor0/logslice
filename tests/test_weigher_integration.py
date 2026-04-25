"""Integration tests: weigher combined with filter and sorter."""
from datetime import datetime, timezone
from logslice.parser import LogLine
from logslice.filter import filter_lines
from logslice.weigher import WeightRule, weigh_lines, format_weighed


def dt(hour: int) -> datetime:
    return datetime(2024, 1, 1, hour, 0, 0, tzinfo=timezone.utc)


def make_line(msg: str, number: int = 1, level: str = None, ts=None) -> LogLine:
    return LogLine(
        raw=msg,
        message=msg,
        timestamp=ts,
        level=level,
        line_number=number,
    )


def _mixed_lines():
    return [
        make_line("startup complete", 1, level="INFO", ts=dt(8)),
        make_line("error: disk full", 2, level="ERROR", ts=dt(9)),
        make_line("warn: low memory", 3, level="WARN", ts=dt(10)),
        make_line("error: timeout", 4, level="ERROR", ts=dt(11)),
        make_line("info: checkpoint", 5, level="INFO", ts=dt(12)),
    ]


def test_weigh_then_top_contains_errors():
    lines = _mixed_lines()
    rules = [
        WeightRule(predicate=lambda l: "error" in l.message.lower(), weight=10.0),
        WeightRule(predicate=lambda l: "warn" in l.message.lower(), weight=3.0),
    ]
    result = weigh_lines(lines, rules)
    top2 = result.top(2)
    messages = [wl.message for wl in top2]
    assert all("error" in m.lower() for m in messages)


def test_weigh_all_lines_preserved():
    lines = _mixed_lines()
    result = weigh_lines(lines, rules=[])
    assert len(result) == len(lines)


def test_filter_then_weigh_count():
    lines = _mixed_lines()
    filtered = list(filter_lines(lines, pattern="error"))
    rules = [WeightRule(predicate=lambda l: "timeout" in l.message, weight=5.0)]
    result = weigh_lines(filtered, rules)
    assert len(result) == len(filtered)
    above = result.above(4.0)
    assert len(above) == 1
    assert "timeout" in above[0].message


def test_format_weighed_integration_no_error():
    lines = _mixed_lines()
    rules = [WeightRule(predicate=lambda l: bool(l.level == "ERROR"), weight=7.0)]
    result = weigh_lines(lines, rules)
    formatted = format_weighed(result, top_n=3)
    assert len(formatted) == 3
    for line in formatted:
        assert "#" in line

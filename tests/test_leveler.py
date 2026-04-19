import pytest
from datetime import datetime
from logslice.parser import LogLine
from logslice.leveler import filter_by_level, format_leveled, LeveledLine, LEVEL_ORDER


def make_line(msg: str, n: int = 1) -> LogLine:
    return LogLine(raw=msg, message=msg, timestamp=None, line_number=n)


def test_filter_keeps_exact_level():
    lines = [make_line("ERROR something bad", 1)]
    result = filter_by_level(lines, "error")
    assert len(result) == 1
    assert result.dropped == 0


def test_filter_drops_below_min_level():
    lines = [make_line("DEBUG verbose stuff", 1), make_line("ERROR boom", 2)]
    result = filter_by_level(lines, "error")
    assert len(result) == 1
    assert result.lines[0].level == "error"
    assert result.dropped == 1


def test_filter_info_keeps_warning_and_above():
    lines = [
        make_line("debug trace", 1),
        make_line("info startup", 2),
        make_line("warning disk low", 3),
        make_line("error crash", 4),
    ]
    result = filter_by_level(lines, "info")
    assert len(result) == 3
    assert result.dropped == 1


def test_filter_empty_input():
    result = filter_by_level([], "info")
    assert len(result) == 0
    assert result.dropped == 0


def test_filter_unknown_min_level_keeps_all():
    lines = [make_line("debug msg", 1), make_line("info msg", 2)]
    result = filter_by_level(lines, "unknown")
    assert len(result) == 2


def test_leveled_line_properties():
    line = make_line("ERROR oops", 5)
    ll = LeveledLine(log_line=line, level="error")
    assert ll.raw == "ERROR oops"
    assert ll.line_number == 5


def test_format_leveled_output():
    lines = [make_line("error bad thing", 1)]
    result = filter_by_level(lines, "error")
    formatted = format_leveled(result)
    assert len(formatted) == 1
    assert formatted[0].startswith("[ERROR]")


def test_warn_alias_treated_as_warning():
    lines = [make_line("warn disk almost full", 1)]
    result = filter_by_level(lines, "warning")
    assert len(result) == 1
    assert result.lines[0].level == "warn"


def test_critical_above_error():
    assert LEVEL_ORDER["critical"] > LEVEL_ORDER["error"]

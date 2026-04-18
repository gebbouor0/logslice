import pytest
from datetime import datetime
from logslice.parser import LogLine
from logslice.pivotter import PivotTable, pivot_lines, format_pivot, _extract_field


def make_line(msg: str, ts=None, n: int = 1) -> LogLine:
    return LogLine(timestamp=ts, message=msg, raw=msg, line_number=n)


def dt(hour: int) -> datetime:
    return datetime(2024, 1, 15, hour, 0, 0)


def test_pivot_by_level_basic():
    lines = [
        make_line("ERROR something"),
        make_line("INFO startup"),
        make_line("ERROR again"),
        make_line("DEBUG detail"),
    ]
    table = pivot_lines(lines, "level")
    assert "ERROR" in table.groups
    assert len(table.groups["ERROR"]) == 2
    assert len(table.groups["INFO"]) == 1


def test_pivot_by_level_unknown_goes_to_other():
    lines = [make_line("just some text")]
    table = pivot_lines(lines, "level", default_key="OTHER")
    assert "OTHER" in table.groups
    assert len(table.groups["OTHER"]) == 1


def test_pivot_by_hour():
    lines = [
        make_line("msg1", ts=dt(10)),
        make_line("msg2", ts=dt(10)),
        make_line("msg3", ts=dt(11)),
    ]
    table = pivot_lines(lines, "hour")
    assert len(table.groups["2024-01-15 10:00"]) == 2
    assert len(table.groups["2024-01-15 11:00"]) == 1


def test_pivot_empty():
    table = pivot_lines([], "level")
    assert len(table) == 0
    assert table.keys() == []


def test_pivot_table_len():
    lines = [make_line("ERROR x"), make_line("INFO y")]
    table = pivot_lines(lines, "level")
    assert len(table) == 2


def test_extract_field_level():
    line = make_line("WARN something bad")
    assert _extract_field(line, "level") == "WARN"


def test_extract_field_unknown_field_returns_none():
    line = make_line("hello")
    assert _extract_field(line, "source") is None


def test_format_pivot_contains_key():
    lines = [make_line("ERROR boom"), make_line("INFO ok")]
    table = pivot_lines(lines, "level")
    out = format_pivot(table)
    assert "[ERROR]" in out
    assert "[INFO]" in out
    assert "ERROR boom" in out


def test_format_pivot_truncates():
    lines = [make_line(f"ERROR msg{i}") for i in range(10)]
    table = pivot_lines(lines, "level")
    out = format_pivot(table, max_per_group=3)
    assert "and 7 more" in out


def test_pivot_keys_sorted():
    lines = [
        make_line("WARN w"),
        make_line("ERROR e"),
        make_line("INFO i"),
    ]
    table = pivot_lines(lines, "level")
    assert table.keys() == sorted(table.keys())

import pytest
from datetime import datetime
from logslice.parser import LogLine
from logslice.grouper import Group, group_by_field, group_by_level, group_by_hour, format_groups


def make_line(message: str, timestamp=None, line_number: int = 1) -> LogLine:
    return LogLine(message=message, timestamp=timestamp, line_number=line_number)


def test_group_by_level_basic():
    lines = [
        make_line("INFO service started"),
        make_line("ERROR something failed"),
        make_line("INFO request received"),
    ]
    groups = group_by_level(lines)
    assert "INFO" in groups
    assert "ERROR" in groups
    assert len(groups["INFO"]) == 2
    assert len(groups["ERROR"]) == 1


def test_group_by_level_unknown():
    lines = [make_line("no level here")]
    groups = group_by_level(lines)
    assert "UNKNOWN" in groups
    assert len(groups["UNKNOWN"]) == 1


def test_group_by_level_case_insensitive():
    lines = [make_line("warning: disk space low"), make_line("WARNING disk full")]
    groups = group_by_level(lines)
    assert "WARNING" in groups
    assert len(groups["WARNING"]) == 2


def test_group_by_hour_basic():
    lines = [
        make_line("msg1", timestamp=datetime(2024, 1, 1, 10, 5)),
        make_line("msg2", timestamp=datetime(2024, 1, 1, 10, 45)),
        make_line("msg3", timestamp=datetime(2024, 1, 1, 11, 0)),
    ]
    groups = group_by_hour(lines)
    assert "2024-01-01 10:00" in groups
    assert "2024-01-01 11:00" in groups
    assert len(groups["2024-01-01 10:00"]) == 2


def test_group_by_hour_no_timestamp():
    lines = [make_line("no ts")]
    groups = group_by_hour(lines)
    assert "(no timestamp)" in groups


def test_group_by_field_custom():
    lines = [
        make_line("user=alice action=login"),
        make_line("user=bob action=logout"),
        make_line("user=alice action=view"),
    ]
    import re
    user_re = re.compile(r'user=(\w+)')

    def get_user(line):
        m = user_re.search(line.message)
        return m.group(1) if m else None

    groups = group_by_field(lines, get_user)
    assert "alice" in groups
    assert "bob" in groups
    assert len(groups["alice"]) == 2


def test_format_groups_output():
    lines = [make_line("INFO started"), make_line("ERROR failed")]
    groups = group_by_level(lines)
    output = format_groups(groups)
    assert "[ERROR]" in output
    assert "[INFO]" in output
    assert "ERROR failed" in output


def test_group_len():
    g = Group(key="test", lines=[make_line("a"), make_line("b")])
    assert len(g) == 2

import pytest
from logslice.parser import LogLine
from logslice.joiner import JoinedRow, join_streams, format_joined


def make_line(message: str, line_number: int = 1) -> LogLine:
    return LogLine(raw=message, message=message, timestamp=None, line_number=line_number)


def test_join_inner_matching_levels():
    left = [make_line("ERROR something", 1), make_line("INFO hello", 2)]
    right = [make_line("ERROR other", 3), make_line("DEBUG nope", 4)]
    rows = join_streams(left, right, field_name="level", how="inner")
    keys = [r.key for r in rows]
    assert "ERROR" in keys
    assert "INFO" not in keys
    assert "DEBUG" not in keys


def test_join_inner_no_match():
    left = [make_line("INFO hello", 1)]
    right = [make_line("ERROR world", 2)]
    rows = join_streams(left, right, field_name="level", how="inner")
    assert rows == []


def test_join_left_includes_unmatched_left():
    left = [make_line("INFO hello", 1), make_line("WARNING watch", 2)]
    right = [make_line("INFO world", 3)]
    rows = join_streams(left, right, field_name="level", how="left")
    keys = {r.key for r in rows}
    assert "INFO" in keys
    assert "WARNING" in keys


def test_join_right_includes_unmatched_right():
    left = [make_line("INFO hello", 1)]
    right = [make_line("INFO world", 2), make_line("ERROR boom", 3)]
    rows = join_streams(left, right, field_name="level", how="right")
    keys = {r.key for r in rows}
    assert "INFO" in keys
    assert "ERROR" in keys


def test_join_outer_all_keys():
    left = [make_line("INFO hello", 1)]
    right = [make_line("ERROR boom", 2)]
    rows = join_streams(left, right, field_name="level", how="outer")
    keys = {r.key for r in rows}
    assert "INFO" in keys
    assert "ERROR" in keys


def test_join_row_messages():
    left = [make_line("ERROR left msg", 1)]
    right = [make_line("ERROR right msg", 2)]
    rows = join_streams(left, right, field_name="level", how="inner")
    assert len(rows) == 1
    assert rows[0].left_message == "ERROR left msg"
    assert rows[0].right_message == "ERROR right msg"


def test_join_empty_streams():
    rows = join_streams([], [], field_name="level", how="outer")
    assert rows == []


def test_format_joined_output():
    left = [make_line("ERROR oops", 1)]
    right = [make_line("ERROR also", 2)]
    rows = join_streams(left, right, field_name="level", how="inner")
    lines = format_joined(rows)
    assert len(lines) == 1
    assert "ERROR" in lines[0]
    assert "LEFT=" in lines[0]
    assert "RIGHT=" in lines[0]


def test_join_multiple_matches_cross_product():
    left = [make_line("INFO a", 1), make_line("INFO b", 2)]
    right = [make_line("INFO c", 3), make_line("INFO d", 4)]
    rows = join_streams(left, right, field_name="level", how="inner")
    assert len(rows) == 4

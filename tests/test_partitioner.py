"""Tests for logslice/partitioner.py"""
import pytest
from datetime import datetime
from logslice.parser import LogLine
from logslice.partitioner import (
    Partition,
    PartitionResult,
    partition_by_pattern,
    partition_by_field,
    partition_by_level,
    format_partitions,
)


def make_line(msg: str, lineno: int = 1, ts=None) -> LogLine:
    return LogLine(raw=msg, message=msg, line_number=lineno, timestamp=ts)


def test_partition_by_pattern_basic():
    lines = [make_line("ERROR something broke"), make_line("INFO all good")]
    result = partition_by_pattern(lines, {"errors": r"ERROR", "info": r"INFO"})
    assert "errors" in result.partitions
    assert "info" in result.partitions
    assert len(result.partitions["errors"]) == 1
    assert len(result.partitions["info"]) == 1


def test_partition_by_pattern_no_match_goes_to_unmatched():
    lines = [make_line("DEBUG verbose stuff")]
    result = partition_by_pattern(lines, {"errors": r"ERROR"})
    assert len(result.unmatched) == 1
    assert len(result.partitions) == 0


def test_partition_by_pattern_default_partition():
    lines = [make_line("DEBUG verbose")]
    result = partition_by_pattern(lines, {"errors": r"ERROR"}, default_partition="other")
    assert "other" in result.partitions
    assert len(result.unmatched) == 0


def test_partition_by_pattern_first_rule_wins():
    lines = [make_line("ERROR critical failure")]
    result = partition_by_pattern(lines, {"errors": r"ERROR", "critical": r"critical"})
    assert len(result.partitions["errors"]) == 1
    assert "critical" not in result.partitions


def test_partition_by_pattern_empty_input():
    result = partition_by_pattern([], {"errors": r"ERROR"})
    assert len(result) == 0
    assert result.total_lines == 0


def test_partition_by_field_basic():
    lines = [make_line("hello"), make_line("world"), make_line("hello again")]
    result = partition_by_field(lines, lambda ln: ln.message.split()[0])
    assert "hello" in result.partitions
    assert "world" in result.partitions
    assert len(result.partitions["hello"]) == 2


def test_partition_by_level_groups_correctly():
    lines = [
        make_line("INFO startup complete"),
        make_line("ERROR disk full"),
        make_line("INFO request received"),
        make_line("WARNING high memory"),
    ]
    result = partition_by_level(lines)
    assert len(result.partitions["INFO"]) == 2
    assert len(result.partitions["ERROR"]) == 1
    assert len(result.partitions["WARNING"]) == 1


def test_partition_by_level_unknown():
    lines = [make_line("something happened")]
    result = partition_by_level(lines)
    assert "UNKNOWN" in result.partitions


def test_total_lines_includes_unmatched():
    lines = [make_line("ERROR x"), make_line("DEBUG y")]
    result = partition_by_pattern(lines, {"errors": r"ERROR"})
    assert result.total_lines == 2


def test_get_returns_partition():
    lines = [make_line("ERROR x")]
    result = partition_by_pattern(lines, {"errors": r"ERROR"})
    p = result.get("errors")
    assert p is not None
    assert len(p) == 1


def test_get_missing_returns_none():
    result = partition_by_pattern([], {})
    assert result.get("nope") is None


def test_format_partitions_output():
    lines = [make_line("ERROR x"), make_line("INFO y")]
    result = partition_by_pattern(lines, {"errors": r"ERROR", "info": r"INFO"})
    out = format_partitions(result)
    assert "errors" in out
    assert "info" in out
    assert "1 line(s)" in out


def test_format_partitions_shows_unmatched():
    lines = [make_line("DEBUG z")]
    result = partition_by_pattern(lines, {})
    out = format_partitions(result)
    assert "unmatched" in out

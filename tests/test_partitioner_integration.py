"""Integration tests: partition then format or combine with other modules."""
import pytest
from logslice.parser import LogLine
from logslice.partitioner import (
    partition_by_pattern,
    partition_by_level,
    format_partitions,
)
from logslice.formatter import FormatOptions, format_lines


def make_line(msg: str, lineno: int = 1) -> LogLine:
    return LogLine(raw=msg, message=msg, line_number=lineno, timestamp=None)


def _make_mixed_lines():
    return [
        make_line("ERROR connection refused", 1),
        make_line("INFO server started", 2),
        make_line("ERROR timeout", 3),
        make_line("WARNING slow query", 4),
        make_line("INFO request ok", 5),
        make_line("DEBUG verbose detail", 6),
    ]


def test_partition_total_lines_preserved():
    lines = _make_mixed_lines()
    result = partition_by_level(lines)
    assert result.total_lines == len(lines)


def test_partition_then_format_each_partition():
    lines = _make_mixed_lines()
    result = partition_by_level(lines)
    opts = FormatOptions(show_line_number=True, show_timestamp=False)
    for name, partition in result.partitions.items():
        formatted = format_lines(partition.lines, opts)
        assert len(formatted) == len(partition.lines)


def test_partition_by_pattern_and_level_consistent():
    lines = _make_mixed_lines()
    pat_result = partition_by_pattern(
        lines,
        {"ERROR": r"\bERROR\b", "INFO": r"\bINFO\b", "WARNING": r"\bWARNING\b"},
        default_partition="OTHER",
    )
    lvl_result = partition_by_level(lines)
    assert len(pat_result.partitions.get("ERROR", [])) == len(
        lvl_result.partitions.get("ERROR", [])
    )


def test_format_partitions_no_error_on_empty():
    result = partition_by_pattern([], {})
    out = format_partitions(result)
    assert isinstance(out, str)


def test_partition_unmatched_count():
    lines = _make_mixed_lines()
    result = partition_by_pattern(lines, {"errors": r"ERROR"})
    matched = len(result.partitions.get("errors", []))
    assert matched + len(result.unmatched) == len(lines)

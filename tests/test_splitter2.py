"""tests for logslice.splitter2"""
from datetime import datetime, timezone
from typing import Optional

import pytest

from logslice.parser import LogLine
from logslice.splitter2 import (
    split_by_duration,
    split_by_delimiter,
    format_blocks,
    BlockResult,
)


def make_line(
    msg: str,
    line_number: int = 1,
    ts: Optional[datetime] = None,
) -> LogLine:
    return LogLine(
        raw=msg,
        message=msg,
        timestamp=ts,
        level=None,
        line_number=line_number,
    )


def dt(second: int) -> datetime:
    return datetime(2024, 1, 1, 0, 0, second, tzinfo=timezone.utc)


# --- split_by_duration ---

def test_split_by_duration_empty():
    result = split_by_duration([], interval_seconds=60)
    assert len(result) == 0
    assert result.total_lines == 0


def test_split_by_duration_single_block():
    lines = [make_line(f"msg {i}", i, dt(i * 5)) for i in range(1, 4)]
    result = split_by_duration(lines, interval_seconds=60)
    assert len(result) == 1
    assert len(result.blocks[0]) == 3


def test_split_by_duration_two_blocks():
    lines = [
        make_line("a", 1, dt(0)),
        make_line("b", 2, dt(30)),
        make_line("c", 3, dt(61)),
        make_line("d", 4, dt(90)),
    ]
    result = split_by_duration(lines, interval_seconds=60)
    assert len(result) == 2
    assert len(result.blocks[0]) == 2
    assert len(result.blocks[1]) == 2


def test_split_by_duration_no_timestamp_appended_to_current():
    lines = [
        make_line("a", 1, dt(0)),
        make_line("no-ts", 2, None),
    ]
    result = split_by_duration(lines, interval_seconds=60)
    assert len(result) == 1
    assert result.total_lines == 2


def test_split_by_duration_invalid_interval():
    with pytest.raises(ValueError):
        split_by_duration([], interval_seconds=0)


# --- split_by_delimiter ---

def test_split_by_delimiter_basic():
    lines = [
        make_line("START", 1),
        make_line("data", 2),
        make_line("START", 3),
        make_line("more", 4),
    ]
    result = split_by_delimiter(lines, pattern=r"START")
    assert len(result) == 2
    assert result.blocks[0].lines[0].message == "START"


def test_split_by_delimiter_no_match_single_block():
    lines = [make_line(f"line {i}", i) for i in range(1, 4)]
    result = split_by_delimiter(lines, pattern=r"NEVER")
    assert len(result) == 1
    assert result.total_lines == 3


def test_split_by_delimiter_exclude_delimiter():
    lines = [
        make_line("---", 1),
        make_line("body", 2),
    ]
    result = split_by_delimiter(lines, pattern=r"---", include_delimiter=False)
    assert len(result.blocks[0]) == 1
    assert result.blocks[0].lines[0].message == "body"


def test_split_by_delimiter_empty():
    result = split_by_delimiter([], pattern=r"START")
    assert len(result) == 0


# --- format_blocks ---

def test_format_blocks_contains_block_name():
    lines = [make_line("hello", 1, dt(0))]
    result = split_by_duration(lines, interval_seconds=60)
    output = format_blocks(result)
    assert "block-1" in output
    assert "hello" in output


def test_format_blocks_empty():
    result = BlockResult()
    output = format_blocks(result)
    assert output == ""

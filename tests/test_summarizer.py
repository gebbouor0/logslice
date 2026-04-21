"""Tests for logslice.summarizer."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

import pytest

from logslice.parser import LogLine
from logslice.summarizer import (
    SummaryBlock,
    SummaryResult,
    format_summary,
    summarize_lines,
)


def make_line(
    message: str,
    line_number: int = 1,
    timestamp: Optional[datetime] = None,
) -> LogLine:
    return LogLine(
        raw=message,
        message=message,
        timestamp=timestamp,
        line_number=line_number,
    )


def dt(hour: int, minute: int = 0) -> datetime:
    return datetime(2024, 1, 1, hour, minute)


def make_lines(n: int, with_ts: bool = False) -> list:
    return [
        make_line(f"msg {i}", i, dt(i % 24) if with_ts else None)
        for i in range(1, n + 1)
    ]


# --- summarize_lines ---

def test_summarize_basic_block_count():
    lines = make_lines(25)
    result = summarize_lines(lines, group_size=10)
    assert len(result) == 3  # 10 + 10 + 5


def test_summarize_total_input():
    lines = make_lines(7)
    result = summarize_lines(lines, group_size=3)
    assert result.total_input == 7


def test_summarize_block_count_field():
    lines = make_lines(10)
    result = summarize_lines(lines, group_size=10)
    assert result.blocks[0].count == 10


def test_summarize_first_and_last_message():
    lines = make_lines(5)
    result = summarize_lines(lines, group_size=5)
    block = result.blocks[0]
    assert block.first_message == "msg 1"
    assert block.last_message == "msg 5"


def test_summarize_label_format():
    lines = make_lines(10)
    result = summarize_lines(lines, group_size=5)
    assert result.blocks[0].label == "lines 1-5"
    assert result.blocks[1].label == "lines 6-10"


def test_summarize_timestamps_none_when_absent():
    lines = make_lines(4)
    result = summarize_lines(lines, group_size=4)
    block = result.blocks[0]
    assert block.first_timestamp is None
    assert block.last_timestamp is None


def test_summarize_timestamps_present():
    lines = make_lines(3, with_ts=True)
    result = summarize_lines(lines, group_size=3)
    block = result.blocks[0]
    assert block.first_timestamp is not None
    assert block.last_timestamp is not None


def test_summarize_sample_lines_count():
    lines = make_lines(10)
    result = summarize_lines(lines, group_size=10, sample_count=3)
    assert len(result.blocks[0].sample_lines) == 3


def test_summarize_sample_zero():
    lines = make_lines(5)
    result = summarize_lines(lines, group_size=5, sample_count=0)
    assert result.blocks[0].sample_lines == []


def test_summarize_empty_input():
    result = summarize_lines([])
    assert len(result) == 0
    assert result.total_input == 0


def test_summarize_invalid_group_size():
    with pytest.raises(ValueError):
        summarize_lines(make_lines(5), group_size=0)


def test_summarize_invalid_sample_count():
    with pytest.raises(ValueError):
        summarize_lines(make_lines(5), sample_count=-1)


# --- format_summary ---

def test_format_summary_contains_header():
    result = summarize_lines(make_lines(5), group_size=5)
    text = format_summary(result)
    assert "Summary:" in text
    assert "5 lines" in text


def test_format_summary_contains_block_label():
    result = summarize_lines(make_lines(5), group_size=5)
    text = format_summary(result)
    assert "lines 1-5" in text


def test_format_summary_contains_messages():
    result = summarize_lines(make_lines(3), group_size=3)
    text = format_summary(result)
    assert "msg 1" in text
    assert "msg 3" in text

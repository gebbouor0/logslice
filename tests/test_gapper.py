"""Tests for logslice.gapper."""
from datetime import datetime, timedelta, timezone
from typing import Optional

import pytest

from logslice.parser import LogLine
from logslice.gapper import detect_gaps, format_gaps, Gap, GapResult


def make_line(
    line_number: int,
    message: str = "msg",
    ts: Optional[datetime] = None,
) -> LogLine:
    return LogLine(raw=message, line_number=line_number, timestamp=ts, message=message)


def dt(offset_seconds: float) -> datetime:
    base = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    return base + timedelta(seconds=offset_seconds)


# --- detect_gaps ---

def test_detect_no_gaps_empty_input():
    result = detect_gaps([])
    assert len(result) == 0
    assert result.total_lines == 0


def test_detect_no_gaps_single_line():
    result = detect_gaps([make_line(1, ts=dt(0))])
    assert len(result) == 0


def test_detect_gap_between_two_lines():
    lines = [make_line(1, ts=dt(0)), make_line(2, ts=dt(30))]
    result = detect_gaps(lines, min_seconds=0)
    assert len(result) == 1
    assert result.gaps[0].seconds == pytest.approx(30.0)


def test_detect_gap_references_correct_lines():
    lines = [make_line(1, ts=dt(0)), make_line(2, ts=dt(60))]
    result = detect_gaps(lines)
    gap = result.gaps[0]
    assert gap.before_line.line_number == 1
    assert gap.after_line.line_number == 2


def test_detect_min_seconds_filters_small_gaps():
    lines = [
        make_line(1, ts=dt(0)),
        make_line(2, ts=dt(5)),
        make_line(3, ts=dt(70)),
    ]
    result = detect_gaps(lines, min_seconds=10)
    assert len(result) == 1
    assert result.gaps[0].seconds == pytest.approx(65.0)


def test_detect_skips_lines_without_timestamp():
    lines = [
        make_line(1, ts=dt(0)),
        make_line(2, ts=None),
        make_line(3, ts=dt(100)),
    ]
    result = detect_gaps(lines, min_seconds=0)
    assert result.skipped_no_timestamp == 1
    # gap should be between line 1 and line 3
    assert len(result) == 1
    assert result.gaps[0].before_line.line_number == 1
    assert result.gaps[0].after_line.line_number == 3


def test_detect_multiple_gaps():
    lines = [make_line(i, ts=dt(i * 60)) for i in range(4)]
    result = detect_gaps(lines, min_seconds=0)
    assert len(result) == 3


def test_largest_gap():
    lines = [
        make_line(1, ts=dt(0)),
        make_line(2, ts=dt(10)),
        make_line(3, ts=dt(200)),
    ]
    result = detect_gaps(lines, min_seconds=0)
    assert result.largest is not None
    assert result.largest.seconds == pytest.approx(190.0)


def test_smallest_gap():
    lines = [
        make_line(1, ts=dt(0)),
        make_line(2, ts=dt(10)),
        make_line(3, ts=dt(200)),
    ]
    result = detect_gaps(lines, min_seconds=0)
    assert result.smallest is not None
    assert result.smallest.seconds == pytest.approx(10.0)


def test_largest_smallest_none_when_no_gaps():
    result = GapResult()
    assert result.largest is None
    assert result.smallest is None


# --- format_gaps ---

def test_format_gaps_no_gaps_message():
    result = GapResult()
    output = format_gaps(result)
    assert output == ["No gaps detected."]


def test_format_gaps_includes_line_numbers():
    lines = [make_line(1, ts=dt(0)), make_line(5, ts=dt(90))]
    result = detect_gaps(lines, min_seconds=0)
    output = format_gaps(result)
    assert any("1" in row and "5" in row for row in output)


def test_format_gaps_total_line_present():
    lines = [make_line(1, ts=dt(0)), make_line(2, ts=dt(30))]
    result = detect_gaps(lines, min_seconds=0)
    output = format_gaps(result)
    assert any("Total gaps" in row for row in output)

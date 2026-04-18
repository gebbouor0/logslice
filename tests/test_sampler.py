"""Tests for logslice.sampler."""

from __future__ import annotations

import pytest
from datetime import datetime
from logslice.parser import LogLine
from logslice.sampler import sample_every_nth, sample_random, sample_lines


def make_line(n: int) -> LogLine:
    return LogLine(
        raw=f"line {n}",
        timestamp=datetime(2024, 1, 1, 0, 0, n % 60),
        level=None,
        message=f"line {n}",
        line_number=n,
    )


LINES = [make_line(i) for i in range(10)]


def test_every_nth_basic():
    result = sample_every_nth(LINES, 3)
    assert result.sample_size == 4  # indices 0,3,6,9
    assert [l.line_number for l in result.lines] == [0, 3, 6, 9]


def test_every_nth_one_returns_all():
    result = sample_every_nth(LINES, 1)
    assert result.sample_size == len(LINES)


def test_every_nth_invalid():
    with pytest.raises(ValueError):
        sample_every_nth(LINES, 0)


def test_every_nth_strategy_label():
    result = sample_every_nth(LINES, 2)
    assert result.strategy == "every_nth:2"
    assert result.total_input == 10


def test_random_sample_count():
    result = sample_random(LINES, 5, seed=42)
    assert result.sample_size == 5
    assert result.strategy == "random"


def test_random_sample_order_preserved():
    result = sample_random(LINES, 5, seed=0)
    nums = [l.line_number for l in result.lines]
    assert nums == sorted(nums)


def test_random_sample_exceeds_available():
    result = sample_random(LINES, 999, seed=1)
    assert result.sample_size == len(LINES)


def test_random_sample_seed_reproducible():
    r1 = sample_random(LINES, 4, seed=7)
    r2 = sample_random(LINES, 4, seed=7)
    assert [l.line_number for l in r1.lines] == [l.line_number for l in r2.lines]


def test_sample_lines_dispatches_nth():
    result = sample_lines(LINES, every_nth=5)
    assert result.strategy == "every_nth:5"


def test_sample_lines_dispatches_random():
    result = sample_lines(LINES, count=3, seed=1)
    assert result.strategy == "random"
    assert result.sample_size == 3


def test_sample_lines_both_raises():
    with pytest.raises(ValueError):
        sample_lines(LINES, every_nth=2, count=3)


def test_sample_lines_neither_raises():
    with pytest.raises(ValueError):
        sample_lines(LINES)

"""Tests for logslice.replayer."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

import pytest

from logslice.parser import LogLine
from logslice.replayer import (
    ReplayEvent,
    ReplayResult,
    build_replay,
    replay_lines,
)


def dt(offset_seconds: float) -> datetime:
    base = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    from datetime import timedelta
    return base + timedelta(seconds=offset_seconds)


def make_line(msg: str, ts: Optional[datetime] = None, n: int = 1) -> LogLine:
    return LogLine(raw=msg, message=msg, timestamp=ts, line_number=n)


# --- build_replay ---

def test_build_replay_empty():
    result = build_replay([])
    assert len(result) == 0
    assert result.skipped == 0


def test_build_replay_skips_no_timestamp():
    lines = [make_line("no ts"), make_line("also no ts")]
    result = build_replay(lines)
    assert len(result) == 0
    assert result.skipped == 2


def test_build_replay_first_event_has_zero_delay():
    lines = [make_line("a", dt(0)), make_line("b", dt(5))]
    result = build_replay(lines)
    assert result.events[0].delay_seconds == 0.0
    assert result.events[0].elapsed_seconds == 0.0


def test_build_replay_delay_matches_gap():
    lines = [make_line("a", dt(0)), make_line("b", dt(10))]
    result = build_replay(lines)
    assert result.events[1].delay_seconds == pytest.approx(10.0)
    assert result.events[1].elapsed_seconds == pytest.approx(10.0)


def test_build_replay_speed_halves_delay():
    lines = [make_line("a", dt(0)), make_line("b", dt(10))]
    result = build_replay(lines, speed=2.0)
    assert result.events[1].delay_seconds == pytest.approx(5.0)


def test_build_replay_max_gap_caps_delay():
    lines = [make_line("a", dt(0)), make_line("b", dt(3600))]
    result = build_replay(lines, max_gap_seconds=5.0)
    assert result.events[1].delay_seconds == pytest.approx(5.0)


def test_build_replay_elapsed_accumulates():
    lines = [make_line("a", dt(0)), make_line("b", dt(3)), make_line("c", dt(7))]
    result = build_replay(lines)
    assert result.events[2].elapsed_seconds == pytest.approx(7.0)


def test_build_replay_invalid_speed():
    with pytest.raises(ValueError, match="speed must be positive"):
        build_replay([], speed=0)


def test_build_replay_mixed_ts_and_none():
    lines = [
        make_line("a", dt(0)),
        make_line("no ts"),
        make_line("b", dt(4)),
    ]
    result = build_replay(lines)
    assert len(result) == 2
    assert result.skipped == 1
    assert result.events[1].delay_seconds == pytest.approx(4.0)


def test_replay_lines_callback_called_for_each_event():
    lines = [make_line("a", dt(0)), make_line("b", dt(1))]
    result = build_replay(lines)
    collected = []
    replay_lines(result, lambda e: collected.append(e.raw), live=False)
    assert collected == ["a", "b"]


def test_replay_event_raw_and_line_number():
    line = make_line("hello", dt(0), n=42)
    result = build_replay([line])
    ev = result.events[0]
    assert ev.raw == "hello"
    assert ev.line_number == 42

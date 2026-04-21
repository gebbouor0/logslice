"""Integration tests combining replayer and scheduler."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

from logslice.parser import LogLine
from logslice.replayer import build_replay
from logslice.scheduler import build_schedule, items_due_by


def dt(offset_seconds: float) -> datetime:
    base = datetime(2024, 3, 15, 6, 0, 0, tzinfo=timezone.utc)
    return base + timedelta(seconds=offset_seconds)


def make_line(msg: str, ts: Optional[datetime] = None, n: int = 1) -> LogLine:
    return LogLine(raw=msg, message=msg, timestamp=ts, line_number=n)


ANCHOR = datetime(2024, 3, 15, 7, 0, 0, tzinfo=timezone.utc)


def test_replay_and_schedule_same_event_count():
    lines = [make_line("a", dt(0)), make_line("b", dt(3)), make_line("c", dt(9))]
    replay = build_replay(lines, speed=1.0)
    schedule = build_schedule(lines, anchor=ANCHOR, speed=1.0)
    assert len(replay) == len(schedule)


def test_replay_elapsed_matches_schedule_offset():
    lines = [make_line("a", dt(0)), make_line("b", dt(7))]
    replay = build_replay(lines, speed=1.0)
    schedule = build_schedule(lines, anchor=ANCHOR, speed=1.0)
    for ev, item in zip(replay.events, schedule.items):
        assert abs(ev.elapsed_seconds - item.offset_seconds) < 1e-6


def test_speed_consistency_replay_vs_schedule():
    lines = [make_line("a", dt(0)), make_line("b", dt(100))]
    replay_fast = build_replay(lines, speed=4.0)
    schedule_fast = build_schedule(lines, anchor=ANCHOR, speed=4.0)
    assert replay_fast.events[1].delay_seconds == pytest.approx(
        schedule_fast.items[1].offset_seconds
    )


def test_skipped_lines_consistent():
    lines = [
        make_line("a", dt(0)),
        make_line("no ts"),
        make_line("b", dt(5)),
    ]
    replay = build_replay(lines)
    schedule = build_schedule(lines, anchor=ANCHOR)
    assert replay.skipped == schedule.skipped == 1
    assert len(replay) == len(schedule) == 2


def test_items_due_covers_all_when_cutoff_is_far_future():
    lines = [make_line(f"line {i}", dt(i * 10)) for i in range(5)]
    schedule = build_schedule(lines, anchor=ANCHOR)
    far_future = ANCHOR + timedelta(hours=24)
    due = items_due_by(schedule, far_future)
    assert len(due) == 5


import pytest

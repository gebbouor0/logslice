"""Tests for logslice.scheduler."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

import pytest

from logslice.parser import LogLine
from logslice.scheduler import Schedule, ScheduledItem, build_schedule, items_due_by


def dt(offset_seconds: float) -> datetime:
    base = datetime(2024, 6, 1, 8, 0, 0, tzinfo=timezone.utc)
    return base + timedelta(seconds=offset_seconds)


def make_line(msg: str, ts: Optional[datetime] = None, n: int = 1) -> LogLine:
    return LogLine(raw=msg, message=msg, timestamp=ts, line_number=n)


ANCHOR = datetime(2024, 6, 1, 9, 0, 0, tzinfo=timezone.utc)


def test_build_schedule_empty():
    s = build_schedule([], anchor=ANCHOR)
    assert len(s) == 0
    assert s.skipped == 0


def test_build_schedule_skips_no_timestamp():
    lines = [make_line("x"), make_line("y")]
    s = build_schedule(lines, anchor=ANCHOR)
    assert len(s) == 0
    assert s.skipped == 2


def test_build_schedule_first_item_fires_at_anchor():
    lines = [make_line("a", dt(0))]
    s = build_schedule(lines, anchor=ANCHOR)
    assert s.items[0].fire_at == ANCHOR
    assert s.items[0].offset_seconds == pytest.approx(0.0)


def test_build_schedule_second_item_offset():
    lines = [make_line("a", dt(0)), make_line("b", dt(10))]
    s = build_schedule(lines, anchor=ANCHOR)
    assert s.items[1].offset_seconds == pytest.approx(10.0)
    assert s.items[1].fire_at == ANCHOR + timedelta(seconds=10)


def test_build_schedule_speed_doubles_compresses_offset():
    lines = [make_line("a", dt(0)), make_line("b", dt(20))]
    s = build_schedule(lines, anchor=ANCHOR, speed=2.0)
    assert s.items[1].offset_seconds == pytest.approx(10.0)


def test_build_schedule_invalid_speed():
    with pytest.raises(ValueError):
        build_schedule([], speed=-1.0)


def test_build_schedule_anchor_stored():
    s = build_schedule([], anchor=ANCHOR)
    assert s.anchor == ANCHOR


def test_build_schedule_is_empty():
    s = build_schedule([])
    assert s.is_empty()


def test_items_due_by_returns_subset():
    lines = [make_line("a", dt(0)), make_line("b", dt(5)), make_line("c", dt(15))]
    s = build_schedule(lines, anchor=ANCHOR)
    cutoff = ANCHOR + timedelta(seconds=10)
    due = items_due_by(s, cutoff)
    assert len(due) == 2
    assert due[0].raw == "a"
    assert due[1].raw == "b"


def test_items_due_by_empty_schedule():
    s = build_schedule([])
    due = items_due_by(s, ANCHOR)
    assert due == []


def test_scheduled_item_raw():
    line = make_line("hello", dt(0))
    s = build_schedule([line], anchor=ANCHOR)
    assert s.items[0].raw == "hello"

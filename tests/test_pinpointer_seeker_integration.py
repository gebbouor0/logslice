"""Integration tests combining pinpointer and seeker."""
from datetime import datetime, timezone
from typing import Optional

from logslice.parser import LogLine
from logslice.pinpointer import pinpoint_by_timestamp
from logslice.seeker import seek_lines


def dt(hour: int, minute: int = 0, second: int = 0) -> datetime:
    return datetime(2024, 1, 1, hour, minute, second, tzinfo=timezone.utc)


def make_line(
    msg: str,
    line_number: int = 1,
    timestamp: Optional[datetime] = None,
) -> LogLine:
    return LogLine(
        raw=msg,
        message=msg,
        timestamp=timestamp,
        level=None,
        line_number=line_number,
    )


def _mixed_lines():
    return [
        make_line("INFO start", 1, dt(10, 0, 0)),
        make_line("ERROR boom", 2, dt(10, 0, 5)),
        make_line("INFO ok", 3, dt(10, 0, 10)),
        make_line("ERROR again", 4, dt(10, 0, 20)),
        make_line("INFO end", 5, dt(10, 0, 30)),
    ]


def test_pinpoint_then_seek_finds_same_line():
    lines = _mixed_lines()
    pin = pinpoint_by_timestamp(lines, dt(10, 0, 5))
    assert pin.found
    target_ln = pin.nearest.line_number
    seek = seek_lines(lines, lambda l: l.line_number == target_ln)
    assert seek.hit_count == 1
    assert seek.hits[0].line.message == "ERROR boom"


def test_pinpoint_nearest_is_within_seek_context():
    lines = _mixed_lines()
    pin = pinpoint_by_timestamp(lines, dt(10, 0, 19))
    assert pin.found
    target_ts = pin.nearest.timestamp
    seek = seek_lines(
        lines,
        lambda l: l.timestamp == target_ts,
        before=1,
        after=1,
    )
    assert seek.hit_count == 1
    all_ctx = seek.hits[0].context_before + seek.hits[0].context_after
    assert len(all_ctx) > 0


def test_pinpoint_no_ts_seek_still_works():
    lines = [make_line("no-ts", i) for i in range(5)]
    pin = pinpoint_by_timestamp(lines, dt(10, 0, 0))
    assert not pin.found
    # seeker should still work independently
    seek = seek_lines(lines, lambda l: l.message == "no-ts")
    assert seek.hit_count == 5


def test_total_input_consistent_across_both():
    lines = _mixed_lines()
    pin = pinpoint_by_timestamp(lines, dt(10, 0, 0))
    seek = seek_lines(lines, lambda l: "ERROR" in l.message)
    assert pin.total_input == len(lines)
    assert seek.total_input == len(lines)

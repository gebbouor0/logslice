import pytest
from datetime import datetime
from logslice.parser import LogLine
from logslice.aligner import align_lines, format_aligned, AlignedSlot


def make_line(msg: str, ts=None, ln: int = 1) -> LogLine:
    return LogLine(raw=msg, message=msg, timestamp=ts, line_number=ln)


def dt(h: int, m: int, s: int = 0) -> datetime:
    return datetime(2024, 1, 1, h, m, s)


def test_align_basic_grouping():
    lines = [
        make_line("a", dt(10, 0, 5)),
        make_line("b", dt(10, 0, 45)),
        make_line("c", dt(10, 1, 10)),
    ]
    slots = align_lines(lines, interval_seconds=60)
    assert len(slots) == 2
    assert len(slots[0]) == 2
    assert len(slots[1]) == 1


def test_align_skips_no_timestamp():
    lines = [
        make_line("no-ts", None),
        make_line("has-ts", dt(9, 0, 0)),
    ]
    slots = align_lines(lines, interval_seconds=60)
    assert len(slots) == 1
    assert slots[0].lines[0].message == "has-ts"


def test_align_empty_input():
    assert align_lines([], interval_seconds=60) == []


def test_align_invalid_interval():
    with pytest.raises(ValueError):
        align_lines([], interval_seconds=0)


def test_align_slots_sorted():
    lines = [
        make_line("late", dt(10, 2, 0)),
        make_line("early", dt(10, 0, 0)),
    ]
    slots = align_lines(lines, interval_seconds=60)
    assert slots[0].bucket < slots[1].bucket


def test_align_sub_minute_interval():
    lines = [
        make_line("a", dt(10, 0, 5)),
        make_line("b", dt(10, 0, 20)),
        make_line("c", dt(10, 0, 35)),
    ]
    slots = align_lines(lines, interval_seconds=30)
    assert len(slots) == 2


def test_format_aligned_basic():
    lines = [make_line("hello", dt(10, 0, 0))]
    slots = align_lines(lines, interval_seconds=60)
    out = format_aligned(slots)
    assert "hello" in out
    assert "2024-01-01" in out


def test_format_aligned_empty_slot_hidden():
    slot = AlignedSlot(bucket=dt(10, 0, 0), lines=[])
    out = format_aligned([slot], show_empty=False)
    assert out == ""


def test_format_aligned_empty_slot_shown():
    slot = AlignedSlot(bucket=dt(10, 0, 0), lines=[])
    out = format_aligned([slot], show_empty=True)
    assert "0 lines" in out

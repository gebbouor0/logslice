import pytest
from datetime import datetime, timezone
from logslice.parser import LogLine
from logslice.rotator import RotationSegment, detect_rotations, format_rotations


def dt(hour: int, minute: int = 0) -> datetime:
    return datetime(2024, 1, 1, hour, minute, tzinfo=timezone.utc)


def make_line(raw: str, timestamp=None, line_number: int = 0) -> LogLine:
    return LogLine(raw=raw, timestamp=timestamp, message=raw, line_number=line_number)


def test_detect_no_rotation():
    lines = [
        make_line("a", dt(1), 1),
        make_line("b", dt(2), 2),
        make_line("c", dt(3), 3),
    ]
    segs = detect_rotations(lines)
    assert len(segs) == 1
    assert len(segs[0]) == 3
    assert segs[0].reason == ""


def test_detect_timestamp_reset():
    lines = [
        make_line("a", dt(5), 1),
        make_line("b", dt(6), 2),
        make_line("c", dt(1), 3),  # reset
        make_line("d", dt(2), 4),
    ]
    segs = detect_rotations(lines)
    assert len(segs) == 2
    assert segs[0].reason == "timestamp_reset"
    assert len(segs[0]) == 2
    assert len(segs[1]) == 2


def test_detect_line_number_reset():
    lines = [
        make_line("a", None, 10),
        make_line("b", None, 11),
        make_line("c", None, 1),  # reset
        make_line("d", None, 2),
    ]
    segs = detect_rotations(lines)
    assert len(segs) == 2
    assert segs[0].reason == "line_number_reset"


def test_detect_empty():
    assert detect_rotations([]) == []


def test_detect_single_line():
    lines = [make_line("only", dt(1), 1)]
    segs = detect_rotations(lines)
    assert len(segs) == 1
    assert len(segs[0]) == 1


def test_segment_index_increments():
    lines = [
        make_line("a", dt(5), 1),
        make_line("b", dt(1), 2),  # reset
        make_line("c", dt(6), 3),
        make_line("d", dt(1), 4),  # reset
    ]
    segs = detect_rotations(lines)
    assert [s.index for s in segs] == [0, 1, 2]


def test_disable_timestamp_detection():
    lines = [
        make_line("a", dt(5), 1),
        make_line("b", dt(1), 2),
    ]
    segs = detect_rotations(lines, detect_timestamp_reset=False)
    assert len(segs) == 1


def test_format_rotations_includes_header():
    lines = [
        make_line("hello", dt(5), 1),
        make_line("world", dt(1), 2),
    ]
    segs = detect_rotations(lines)
    out = format_rotations(segs)
    assert any("Segment 0" in l for l in out)
    assert any("rotation" in l for l in out)
    assert "hello" in out
    assert "world" in out


def test_format_rotations_no_reason_header():
    lines = [make_line("x", dt(1), 1), make_line("y", dt(2), 2)]
    segs = detect_rotations(lines)
    out = format_rotations(segs)
    assert all("rotation" not in l for l in out if l.startswith("==="))

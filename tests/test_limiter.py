import pytest
from datetime import datetime, timezone, timedelta
from logslice.parser import LogLine
from logslice.limiter import limit_head, limit_tail, limit_by_duration, limit_lines


def make_line(n: int, ts=None):
    return LogLine(raw=f"line {n}", line_number=n, timestamp=ts, message=f"msg {n}")


def dt(offset_s: int):
    base = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    return base + timedelta(seconds=offset_s)


def make_lines(count=5):
    return [make_line(i) for i in range(count)]


def test_limit_head_basic():
    lines = make_lines(10)
    result = limit_head(lines, 3)
    assert len(result) == 3
    assert result.dropped == 7
    assert result.strategy == "head"


def test_limit_head_more_than_available():
    lines = make_lines(3)
    result = limit_head(lines, 10)
    assert len(result) == 3
    assert result.dropped == 0


def test_limit_head_zero():
    result = limit_head(make_lines(5), 0)
    assert len(result) == 0
    assert result.dropped == 5


def test_limit_head_negative_raises():
    with pytest.raises(ValueError):
        limit_head(make_lines(5), -1)


def test_limit_tail_basic():
    lines = make_lines(10)
    result = limit_tail(lines, 4)
    assert len(result) == 4
    assert result.lines[0].line_number == 6
    assert result.strategy == "tail"


def test_limit_tail_zero():
    result = limit_tail(make_lines(5), 0)
    assert len(result) == 0


def test_limit_tail_negative_raises():
    with pytest.raises(ValueError):
        limit_tail(make_lines(3), -2)


def test_limit_by_duration_basic():
    lines = [
        make_line(1, dt(0)),
        make_line(2, dt(5)),
        make_line(3, dt(10)),
        make_line(4, dt(20)),
    ]
    result = limit_by_duration(lines, seconds=10)
    assert len(result) == 3
    assert result.dropped == 1


def test_limit_by_duration_from_end():
    lines = [
        make_line(1, dt(0)),
        make_line(2, dt(10)),
        make_line(3, dt(20)),
        make_line(4, dt(25)),
    ]
    result = limit_by_duration(lines, seconds=10, from_end=True)
    assert len(result) == 3
    assert result.lines[0].line_number == 2


def test_limit_by_duration_no_timestamps():
    lines = make_lines(5)
    result = limit_by_duration(lines, seconds=60)
    assert len(result) == 5
    assert result.dropped == 0


def test_limit_lines_dispatches_head():
    result = limit_lines(make_lines(10), strategy="head", n=2)
    assert len(result) == 2


def test_limit_lines_dispatches_tail():
    result = limit_lines(make_lines(10), strategy="tail", n=3)
    assert len(result) == 3


def test_limit_lines_duration_requires_seconds():
    with pytest.raises(ValueError):
        limit_lines(make_lines(5), strategy="duration")


def test_limit_lines_unknown_strategy():
    with pytest.raises(ValueError):
        limit_lines(make_lines(5), strategy="bogus")

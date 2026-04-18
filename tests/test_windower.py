import pytest
from datetime import datetime, timedelta, timezone
from logslice.parser import LogLine
from logslice.windower import Window, window_lines, format_windows


def make_line(msg: str, ts=None, n: int = 1) -> LogLine:
    return LogLine(raw=msg, message=msg, timestamp=ts, line_number=n)


def dt(h: int, m: int = 0) -> datetime:
    return datetime(2024, 1, 1, h, m, tzinfo=timezone.utc)


INTERVAL = timedelta(hours=1)


def test_window_basic_count():
    lines = [
        make_line("a", dt(10), 1),
        make_line("b", dt(10, 30), 2),
        make_line("c", dt(11, 10), 3),
    ]
    windows = window_lines(lines, INTERVAL)
    assert len(windows) == 2
    assert len(windows[0]) == 2
    assert len(windows[1]) == 1


def test_window_start_end():
    lines = [make_line("a", dt(9), 1), make_line("b", dt(9, 45), 2)]
    windows = window_lines(lines, INTERVAL)
    assert windows[0].start == dt(9)
    assert windows[0].end == dt(10)


def test_window_skips_no_timestamp():
    lines = [
        make_line("no-ts", None, 1),
        make_line("has-ts", dt(8), 2),
    ]
    windows = window_lines(lines, INTERVAL)
    assert len(windows) == 1
    assert windows[0].lines[0].message == "has-ts"


def test_window_empty_lines():
    assert window_lines([], INTERVAL) == []


def test_window_all_no_timestamp():
    lines = [make_line("x", None, i) for i in range(3)]
    assert window_lines(lines, INTERVAL) == []


def test_window_invalid_interval():
    with pytest.raises(ValueError):
        window_lines([], timedelta(seconds=0))


def test_window_invalid_slide():
    with pytest.raises(ValueError):
        window_lines([], INTERVAL, slide=timedelta(seconds=-1))


def test_sliding_window_overlap():
    lines = [
        make_line("a", dt(10), 1),
        make_line("b", dt(10, 30), 2),
        make_line("c", dt(11), 3),
    ]
    windows = window_lines(lines, INTERVAL, slide=timedelta(minutes=30))
    # windows: [10,11), [10:30,11:30), [11,12)
    assert len(windows) == 3
    # line b appears in first two windows
    msgs_0 = [l.message for l in windows[0].lines]
    msgs_1 = [l.message for l in windows[1].lines]
    assert "b" in msgs_0
    assert "b" in msgs_1


def test_format_windows_output():
    lines = [make_line("hello", dt(7), 1)]
    windows = window_lines(lines, INTERVAL)
    out = format_windows(windows)
    assert "Window 1" in out
    assert "hello" in out


def test_window_len_dunder():
    w = Window(start=dt(1), end=dt(2), lines=[make_line("x", dt(1), 1)])
    assert len(w) == 1

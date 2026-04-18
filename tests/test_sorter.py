import pytest
from datetime import datetime, timezone
from logslice.parser import LogLine
from logslice.sorter import sort_by_timestamp, sort_by_message, sort_by_line_number, sort_lines


def make_line(message: str, ts=None, line_number: int = 1) -> LogLine:
    return LogLine(raw=message, message=message, timestamp=ts, level=None, line_number=line_number)


def dt(hour: int):
    return datetime(2024, 1, 1, hour, 0, 0, tzinfo=timezone.utc)


def test_sort_by_timestamp_ascending():
    lines = [make_line("c", dt(3)), make_line("a", dt(1)), make_line("b", dt(2))]
    result = sort_by_timestamp(lines)
    assert [l.message for l in result.lines] == ["a", "b", "c"]
    assert result.strategy == "timestamp"
    assert result.reversed is False


def test_sort_by_timestamp_descending():
    lines = [make_line("a", dt(1)), make_line("c", dt(3)), make_line("b", dt(2))]
    result = sort_by_timestamp(lines, reverse=True)
    assert [l.message for l in result.lines] == ["c", "b", "a"]
    assert result.reversed is True


def test_sort_by_timestamp_none_last():
    lines = [make_line("no-ts", None), make_line("has-ts", dt(1))]
    result = sort_by_timestamp(lines)
    assert result.lines[0].message == "has-ts"
    assert result.lines[1].message == "no-ts"


def test_sort_by_message_alphabetical():
    lines = [make_line("Zebra"), make_line("apple"), make_line("Mango")]
    result = sort_by_message(lines)
    assert [l.message for l in result.lines] == ["apple", "Mango", "Zebra"]
    assert result.strategy == "message"


def test_sort_by_message_reverse():
    lines = [make_line("apple"), make_line("Mango"), make_line("Zebra")]
    result = sort_by_message(lines, reverse=True)
    assert result.lines[0].message == "Zebra"


def test_sort_by_line_number():
    lines = [make_line("c", line_number=3), make_line("a", line_number=1), make_line("b", line_number=2)]
    result = sort_by_line_number(lines)
    assert [l.message for l in result.lines] == ["a", "b", "c"]
    assert result.strategy == "line_number"


def test_sort_by_line_number_none_last():
    lines = [make_line("no-num", line_number=None), make_line("has-num", line_number=1)]
    result = sort_by_line_number(lines)
    assert result.lines[0].message == "has-num"


def test_sort_lines_dispatch_timestamp():
    lines = [make_line("b", dt(2)), make_line("a", dt(1))]
    result = sort_lines(lines, strategy="timestamp")
    assert result.lines[0].message == "a"


def test_sort_lines_dispatch_message():
    lines = [make_line("z"), make_line("a")]
    result = sort_lines(lines, strategy="message")
    assert result.lines[0].message == "a"


def test_sort_lines_invalid_strategy():
    with pytest.raises(ValueError, match="Unknown sort strategy"):
        sort_lines([], strategy="bogus")


def test_sort_lines_empty():
    result = sort_lines([], strategy="timestamp")
    assert result.lines == []

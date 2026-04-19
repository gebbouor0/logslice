import pytest
from logslice.parser import LogLine
from logslice.flattener import FlattenedLine, flatten_lines, format_flattened, _is_continuation
from datetime import datetime


def make_line(message: str, timestamp=None, line_number: int = 1) -> LogLine:
    return LogLine(
        raw=message,
        timestamp=timestamp,
        level=None,
        message=message,
        line_number=line_number,
    )


TS = datetime(2024, 1, 1, 12, 0, 0)


def test_is_continuation_with_timestamp_returns_false():
    line = make_line("  indented", timestamp=TS)
    assert _is_continuation(line) is False


def test_is_continuation_indented_no_timestamp():
    line = make_line("  indented detail")
    assert _is_continuation(line) is True


def test_is_continuation_tab_prefix():
    line = make_line("\tcontinued")
    assert _is_continuation(line) is True


def test_is_continuation_dots_prefix():
    line = make_line("...more info")
    assert _is_continuation(line) is True


def test_is_continuation_normal_line():
    line = make_line("normal log entry")
    assert _is_continuation(line) is False


def test_flatten_no_continuations():
    lines = [
        make_line("first", timestamp=TS, line_number=1),
        make_line("second", timestamp=TS, line_number=2),
    ]
    result = flatten_lines(lines)
    assert len(result) == 2
    assert result[0].continuation_count == 0
    assert result[1].continuation_count == 0


def test_flatten_merges_continuation():
    lines = [
        make_line("main entry", timestamp=TS, line_number=1),
        make_line("  detail line", line_number=2),
        make_line("  more detail", line_number=3),
    ]
    result = flatten_lines(lines)
    assert len(result) == 1
    assert result[0].continuation_count == 2
    assert "detail line" in result[0].joined_message
    assert "more detail" in result[0].joined_message


def test_flatten_empty_input():
    assert flatten_lines([]) == []


def test_flatten_preserves_line_number():
    lines = [make_line("entry", timestamp=TS, line_number=5)]
    result = flatten_lines(lines)
    assert result[0].line_number == 5


def test_flatten_as_log_line_message():
    lines = [
        make_line("main", timestamp=TS, line_number=1),
        make_line("  extra", line_number=2),
    ]
    result = flatten_lines(lines)
    log_line = result[0].as_log_line()
    assert "extra" in log_line.message


def test_format_flattened_no_continuations():
    lines = [make_line("hello", timestamp=TS)]
    flat = flatten_lines(lines)
    out = format_flattened(flat)
    assert out == ["hello"]


def test_format_flattened_shows_continuation_count():
    lines = [
        make_line("main", timestamp=TS),
        make_line("  cont"),
    ]
    flat = flatten_lines(lines)
    out = format_flattened(flat)
    assert "[+1 lines]" in out[0]

import pytest
from datetime import datetime
from logslice.parser import LogLine
from logslice.compressor import (
    compress_lines,
    format_compressed,
    CompressResult,
)


def make_line(msg: str, ts=None, ln=1) -> LogLine:
    return LogLine(raw=msg, message=msg, timestamp=ts, line_number=ln)


def dt(hour: int) -> datetime:
    return datetime(2024, 1, 1, hour, 0, 0)


def test_compress_empty():
    result = compress_lines([])
    assert result.total_input == 0
    assert result.total_output == 0
    assert result.ratio == 1.0


def test_compress_no_duplicates():
    lines = [make_line(f"msg{i}") for i in range(3)]
    result = compress_lines(lines)
    assert result.total_output == 3
    assert result.total_input == 3
    assert all(c.count == 1 for c in result.lines)


def test_compress_consecutive_duplicates():
    lines = [make_line("error") for _ in range(4)]
    result = compress_lines(lines)
    assert result.total_output == 1
    assert result.total_input == 4
    assert result.lines[0].count == 4


def test_compress_non_consecutive_not_merged():
    lines = [make_line("a"), make_line("b"), make_line("a")]
    result = compress_lines(lines)
    assert result.total_output == 3


def test_compress_ratio():
    lines = [make_line("x") for _ in range(5)]
    result = compress_lines(lines)
    assert result.ratio == pytest.approx(5.0)


def test_compress_preserves_first_last_seen():
    lines = [
        make_line("err", ts=dt(1)),
        make_line("err", ts=dt(2)),
        make_line("err", ts=dt(3)),
    ]
    result = compress_lines(lines)
    assert len(result.lines) == 1
    assert result.lines[0].first_seen == dt(1)
    assert result.lines[0].last_seen == dt(3)


def test_compress_mixed_groups():
    lines = [
        make_line("a"), make_line("a"),
        make_line("b"),
        make_line("c"), make_line("c"), make_line("c"),
    ]
    result = compress_lines(lines)
    assert result.total_output == 3
    assert result.lines[0].count == 2
    assert result.lines[1].count == 1
    assert result.lines[2].count == 3


def test_format_compressed_single():
    lines = [make_line("hello")]
    result = compress_lines(lines)
    out = format_compressed(result)
    assert out == ["hello"]


def test_format_compressed_repeated():
    lines = [make_line("boom") for _ in range(3)]
    result = compress_lines(lines)
    out = format_compressed(result)
    assert out == ["[x3] boom"]


def test_format_compressed_mixed():
    lines = [make_line("a"), make_line("a"), make_line("b")]
    result = compress_lines(lines)
    out = format_compressed(result)
    assert out == ["[x2] a", "b"]

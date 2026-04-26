"""Tests for logslice.receiver."""
from __future__ import annotations

import io

import pytest

from logslice.receiver import (
    ReceiveResult,
    receive_from_stream,
    receive_from_iterable,
    receive_lines,
)


# ---------------------------------------------------------------------------
# receive_from_stream
# ---------------------------------------------------------------------------

def test_receive_from_stream_basic():
    buf = io.StringIO("2024-01-01T08:00:00 INFO hello\n2024-01-01T09:00:00 ERROR oops\n")
    result = receive_from_stream(buf, source_name="test")
    assert len(result) == 2
    assert result.source_name == "test"


def test_receive_from_stream_skips_blank_lines():
    buf = io.StringIO("line one\n\nline two\n")
    result = receive_from_stream(buf)
    assert len(result) == 2
    assert result.skipped == 1


def test_receive_from_stream_predicate_filters():
    buf = io.StringIO("INFO ok\nERROR bad\nINFO fine\n")
    result = receive_from_stream(buf, predicate=lambda ln: "ERROR" in ln.raw)
    assert len(result) == 1
    assert "ERROR" in result.lines[0].raw


def test_receive_from_stream_empty():
    buf = io.StringIO("")
    result = receive_from_stream(buf)
    assert len(result) == 0


# ---------------------------------------------------------------------------
# receive_from_iterable
# ---------------------------------------------------------------------------

def test_receive_from_iterable_basic():
    lines = ["alpha", "beta", "gamma"]
    result = receive_from_iterable(lines, source_name="list")
    assert len(result) == 3
    assert result.source_name == "list"


def test_receive_from_iterable_strips_newlines():
    lines = ["hello\n", "world\n"]
    result = receive_from_iterable(lines)
    assert result.lines[0].raw == "hello"
    assert result.lines[1].raw == "world"


def test_receive_from_iterable_skips_empty_strings():
    lines = ["a", "", "b", ""]
    result = receive_from_iterable(lines)
    assert len(result) == 2
    assert result.skipped == 2


def test_receive_from_iterable_predicate():
    lines = ["INFO start", "ERROR crash", "INFO end"]
    result = receive_from_iterable(lines, predicate=lambda ln: "INFO" in ln.raw)
    assert len(result) == 2


def test_receive_from_iterable_line_numbers_sequential():
    lines = ["first", "second", "third"]
    result = receive_from_iterable(lines)
    numbers = [ln.line_number for ln in result.lines]
    assert numbers == [1, 2, 3]


# ---------------------------------------------------------------------------
# receive_lines (unified)
# ---------------------------------------------------------------------------

def test_receive_lines_from_stream():
    buf = io.StringIO("hello\nworld\n")
    result = receive_lines(buf, source_name="buf")
    assert len(result) == 2
    assert result.source_name == "buf"


def test_receive_lines_from_iterable():
    result = receive_lines(["a", "b", "c"], source_name="iter")
    assert len(result) == 3


def test_receive_lines_result_is_iterable():
    result = receive_lines(["x", "y"])
    msgs = [ln.raw for ln in result]
    assert msgs == ["x", "y"]


def test_receive_lines_empty_input():
    result = receive_lines([])
    assert len(result) == 0
    assert result.skipped == 0

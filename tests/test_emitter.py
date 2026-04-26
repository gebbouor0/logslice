"""Tests for logslice.emitter."""
from __future__ import annotations

import io
from datetime import datetime

import pytest

from logslice.parser import LogLine
from logslice.emitter import (
    EmitResult,
    emit_to_stream,
    emit_to_callback,
    emit_lines,
)


def make_line(msg: str, n: int = 1, ts: datetime | None = None) -> LogLine:
    raw = f"{ts.isoformat() + ' ' if ts else ''}{msg}"
    return LogLine(raw=raw, line_number=n, timestamp=ts, message=msg)


# ---------------------------------------------------------------------------
# emit_to_stream
# ---------------------------------------------------------------------------

def test_emit_to_stream_basic():
    buf = io.StringIO()
    lines = [make_line("hello", 1), make_line("world", 2)]
    result = emit_to_stream(lines, buf, sink_name="test")
    assert len(result) == 2
    assert result.sink_name == "test"
    output = buf.getvalue()
    assert "hello" in output
    assert "world" in output


def test_emit_to_stream_custom_formatter():
    buf = io.StringIO()
    lines = [make_line("msg", 5)]
    emit_to_stream(lines, buf, formatter=lambda ln: f"[{ln.line_number}] {ln.message}")
    assert buf.getvalue().strip() == "[5] msg"


def test_emit_to_stream_empty():
    buf = io.StringIO()
    result = emit_to_stream([], buf)
    assert len(result) == 0
    assert buf.getvalue() == ""


# ---------------------------------------------------------------------------
# emit_to_callback
# ---------------------------------------------------------------------------

def test_emit_to_callback_collects_all():
    seen = []
    lines = [make_line(f"line {i}", i) for i in range(4)]
    result = emit_to_callback(lines, seen.append, sink_name="cb")
    assert len(result) == 4
    assert len(seen) == 4
    assert result.sink_name == "cb"


def test_emit_to_callback_order_preserved():
    seen = []
    lines = [make_line("a", 1), make_line("b", 2), make_line("c", 3)]
    emit_to_callback(lines, seen.append)
    assert [ln.message for ln in seen] == ["a", "b", "c"]


def test_emit_to_callback_empty():
    calls = []
    result = emit_to_callback([], calls.append)
    assert len(result) == 0
    assert calls == []


# ---------------------------------------------------------------------------
# emit_lines (unified)
# ---------------------------------------------------------------------------

def test_emit_lines_writes_to_stream():
    buf = io.StringIO()
    lines = [make_line("hello", 1)]
    result = emit_lines(lines, stream=buf)
    assert "hello" in buf.getvalue()
    assert len(result) == 1


def test_emit_lines_calls_callback():
    buf = io.StringIO()
    collected = []
    lines = [make_line("x", 1), make_line("y", 2)]
    emit_lines(lines, stream=buf, callback=collected.append)
    assert len(collected) == 2


def test_emit_lines_result_is_iterable():
    buf = io.StringIO()
    lines = [make_line("a", 1), make_line("b", 2)]
    result = emit_lines(lines, stream=buf)
    msgs = [ln.message for ln in result]
    assert msgs == ["a", "b"]


def test_emit_lines_empty_input():
    buf = io.StringIO()
    result = emit_lines([], stream=buf)
    assert len(result) == 0
    assert buf.getvalue() == ""

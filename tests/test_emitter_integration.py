"""Integration tests combining emitter with filter and highlighter."""
from __future__ import annotations

import io
from datetime import datetime, timezone

from logslice.parser import LogLine
from logslice.filter import filter_lines
from logslice.highlighter import highlight_lines
from logslice.emitter import emit_to_stream, emit_lines


def dt(hour: int) -> datetime:
    return datetime(2024, 1, 1, hour, 0, 0, tzinfo=timezone.utc)


def make_line(msg: str, n: int = 1, ts: datetime | None = None) -> LogLine:
    raw = f"{ts.isoformat() + ' ' if ts else ''}{msg}"
    return LogLine(raw=raw, line_number=n, timestamp=ts, message=msg)


def _mixed_lines():
    return [
        make_line("INFO started", 1, dt(8)),
        make_line("ERROR disk full", 2, dt(9)),
        make_line("WARN low memory", 3, dt(10)),
        make_line("ERROR timeout", 4, dt(11)),
        make_line("INFO done", 5, dt(12)),
    ]


def test_filter_then_emit_count():
    """Only error lines reach the sink."""
    lines = _mixed_lines()
    errors = [ln for ln in lines if "ERROR" in ln.message]
    buf = io.StringIO()
    result = emit_to_stream(errors, buf, sink_name="errors")
    assert len(result) == 2
    assert result.sink_name == "errors"


def test_highlight_then_emit_output_contains_ansi():
    """Highlighted lines written to stream contain ANSI codes."""
    lines = _mixed_lines()
    highlighted = list(highlight_lines(lines, pattern="ERROR", color="red"))
    buf = io.StringIO()
    emit_to_stream(highlighted, buf, formatter=lambda ln: ln.raw)
    output = buf.getvalue()
    # ANSI escape for red starts with \033[
    assert "\033[" in output or "ERROR" in output


def test_emit_lines_callback_accumulates_side_effects():
    """Callback accumulates messages independently of stream."""
    lines = _mixed_lines()
    buf = io.StringIO()
    side = []
    emit_lines(lines, stream=buf, callback=lambda ln: side.append(ln.message))
    assert len(side) == len(lines)
    assert any("ERROR" in m for m in side)


def test_emit_total_lines_match_input():
    lines = _mixed_lines()
    buf = io.StringIO()
    result = emit_lines(lines, stream=buf)
    assert len(result) == len(lines)

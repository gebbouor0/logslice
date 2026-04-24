"""Integration tests for fencer — multiple blocks, regex patterns."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from logslice.parser import LogLine
from logslice.fencer import fence_lines, format_fenced


def dt(h: int, m: int = 0) -> datetime:
    return datetime(2024, 1, 1, h, m, tzinfo=timezone.utc)


def make_line(msg: str, n: int, ts: Optional[datetime] = None) -> LogLine:
    return LogLine(raw=msg, message=msg, line_number=n, timestamp=ts, level=None)


def _make_transaction_log():
    return [
        make_line("INFO  system ready", 1, dt(9, 0)),
        make_line("BEGIN TRANSACTION tx-1", 2, dt(9, 1)),
        make_line("UPDATE users SET ...", 3, dt(9, 1)),
        make_line("INSERT INTO orders ...", 4, dt(9, 2)),
        make_line("COMMIT TRANSACTION tx-1", 5, dt(9, 2)),
        make_line("INFO  idle", 6, dt(9, 3)),
        make_line("BEGIN TRANSACTION tx-2", 7, dt(9, 4)),
        make_line("DELETE FROM cache ...", 8, dt(9, 4)),
        make_line("ROLLBACK TRANSACTION tx-2", 9, dt(9, 5)),
        make_line("INFO  shutdown", 10, dt(9, 6)),
    ]


def test_fence_extracts_both_transactions():
    lines = _make_transaction_log()
    result = fence_lines(lines, r"BEGIN TRANSACTION", r"(?:COMMIT|ROLLBACK) TRANSACTION")
    assert len(result) == 2


def test_fence_total_input_preserved():
    lines = _make_transaction_log()
    result = fence_lines(lines, r"BEGIN TRANSACTION", r"(?:COMMIT|ROLLBACK) TRANSACTION")
    assert result.total_input == len(lines)


def test_fence_inner_lines_correct_without_fences():
    lines = _make_transaction_log()
    result = fence_lines(
        lines,
        r"BEGIN TRANSACTION",
        r"(?:COMMIT|ROLLBACK) TRANSACTION",
        include_fences=False,
    )
    # tx-1 has 2 inner lines; tx-2 has 1 inner line
    assert len(result.blocks[0]) == 2
    assert len(result.blocks[1]) == 1


def test_fence_format_output_contains_block_labels():
    lines = _make_transaction_log()
    result = fence_lines(lines, r"BEGIN TRANSACTION", r"(?:COMMIT|ROLLBACK) TRANSACTION")
    out = format_fenced(result)
    assert "block 1" in out
    assert "block 2" in out


def test_fence_all_closed():
    lines = _make_transaction_log()
    result = fence_lines(lines, r"BEGIN TRANSACTION", r"(?:COMMIT|ROLLBACK) TRANSACTION")
    assert all(b.is_closed for b in result.blocks)

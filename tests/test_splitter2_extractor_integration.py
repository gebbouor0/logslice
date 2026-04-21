"""integration: split log into duration blocks then extract fields from each block"""
from datetime import datetime, timezone
from typing import Optional

from logslice.parser import LogLine
from logslice.splitter2 import split_by_duration
from logslice.extractor import extract_fields


def dt(second: int) -> datetime:
    return datetime(2024, 1, 1, 0, 0, second, tzinfo=timezone.utc)


def make_line(
    msg: str,
    line_number: int,
    ts: Optional[datetime] = None,
) -> LogLine:
    return LogLine(
        raw=msg,
        message=msg,
        timestamp=ts,
        level=None,
        line_number=line_number,
    )


LINES = [
    make_line("user=alice action=login", 1, dt(0)),
    make_line("user=bob action=view", 2, dt(10)),
    make_line("heartbeat ok", 3, dt(20)),
    make_line("user=carol action=logout", 4, dt(70)),
    make_line("user=dave action=login", 5, dt(80)),
]

PATTERN = r"user=(?P<user>\w+)\s+action=(?P<action>\w+)"


def test_split_then_extract_block_counts():
    blocks = split_by_duration(LINES, interval_seconds=60)
    assert len(blocks) == 2


def test_split_then_extract_matched_per_block():
    blocks = split_by_duration(LINES, interval_seconds=60)
    block0_result = extract_fields(blocks.blocks[0].lines, PATTERN)
    block1_result = extract_fields(blocks.blocks[1].lines, PATTERN)
    # block 0: alice login, bob view, heartbeat (no match)
    assert len(block0_result.matched) == 2
    assert len(block0_result.unmatched) == 1
    # block 1: carol logout, dave login
    assert len(block1_result.matched) == 2


def test_split_then_extract_total_lines_preserved():
    blocks = split_by_duration(LINES, interval_seconds=60)
    total = sum(
        len(extract_fields(b.lines, PATTERN))
        for b in blocks.blocks
    )
    assert total == len(LINES)


def test_column_users_across_blocks():
    blocks = split_by_duration(LINES, interval_seconds=60)
    all_users = []
    for b in blocks.blocks:
        result = extract_fields(b.lines, PATTERN)
        all_users.extend(u for u in result.column("user") if u is not None)
    assert set(all_users) == {"alice", "bob", "carol", "dave"}

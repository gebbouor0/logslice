"""segment log lines into fixed-duration time windows or pattern-delimited blocks"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import timedelta
from typing import List, Optional
import re

from logslice.parser import LogLine


@dataclass
class Block:
    name: str
    lines: List[LogLine] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.lines)


@dataclass
class BlockResult:
    blocks: List[Block] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.blocks)

    @property
    def total_lines(self) -> int:
        return sum(len(b) for b in self.blocks)


def split_by_duration(
    lines: List[LogLine],
    interval_seconds: int = 60,
) -> BlockResult:
    """Split lines into blocks based on timestamp intervals."""
    if interval_seconds <= 0:
        raise ValueError("interval_seconds must be positive")

    result = BlockResult()
    current: Optional[Block] = None
    boundary = None
    delta = timedelta(seconds=interval_seconds)

    for line in lines:
        if line.timestamp is None:
            if current is None:
                current = Block(name="block-1")
                result.blocks.append(current)
            current.lines.append(line)
            continue

        if boundary is None or line.timestamp >= boundary:
            boundary = line.timestamp + delta
            idx = len(result.blocks) + 1
            current = Block(name=f"block-{idx}")
            result.blocks.append(current)

        current.lines.append(line)  # type: ignore[union-attr]

    return result


def split_by_delimiter(
    lines: List[LogLine],
    pattern: str,
    include_delimiter: bool = True,
) -> BlockResult:
    """Split lines into blocks each time a line matches *pattern*."""
    rx = re.compile(pattern)
    result = BlockResult()
    current: Optional[Block] = None

    for line in lines:
        if rx.search(line.message):
            current = Block(name=f"block-{len(result.blocks) + 1}")
            result.blocks.append(current)
            if include_delimiter:
                current.lines.append(line)
        else:
            if current is None:
                current = Block(name="block-1")
                result.blocks.append(current)
            current.lines.append(line)

    return result


def format_blocks(result: BlockResult) -> str:
    parts: List[str] = []
    for block in result.blocks:
        parts.append(f"=== {block.name} ({len(block)} lines) ===")
        for line in block.lines:
            parts.append(f"  [{line.line_number}] {line.message}")
    return "\n".join(parts)

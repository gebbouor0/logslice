"""Summarize log lines into condensed human-readable blocks."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from logslice.parser import LogLine


@dataclass
class SummaryBlock:
    label: str
    count: int
    first_message: str
    last_message: str
    first_timestamp: Optional[str]
    last_timestamp: Optional[str]
    sample_lines: List[LogLine] = field(default_factory=list)

    def __len__(self) -> int:
        return self.count


@dataclass
class SummaryResult:
    blocks: List[SummaryBlock]
    total_input: int

    def __len__(self) -> int:
        return len(self.blocks)


def summarize_lines(
    lines: List[LogLine],
    group_size: int = 10,
    sample_count: int = 2,
) -> SummaryResult:
    """Group lines into fixed-size blocks and produce a summary per block."""
    if group_size < 1:
        raise ValueError("group_size must be >= 1")
    if sample_count < 0:
        raise ValueError("sample_count must be >= 0")

    blocks: List[SummaryBlock] = []
    total = len(lines)

    for start in range(0, total, group_size):
        chunk = lines[start : start + group_size]
        label = f"lines {start + 1}-{start + len(chunk)}"
        timestamps = [l.timestamp.isoformat() for l in chunk if l.timestamp]
        samples = chunk[:sample_count]
        block = SummaryBlock(
            label=label,
            count=len(chunk),
            first_message=chunk[0].message,
            last_message=chunk[-1].message,
            first_timestamp=timestamps[0] if timestamps else None,
            last_timestamp=timestamps[-1] if timestamps else None,
            sample_lines=samples,
        )
        blocks.append(block)

    return SummaryResult(blocks=blocks, total_input=total)


def format_summary(result: SummaryResult) -> str:
    """Render a SummaryResult as a plain-text report."""
    lines: List[str] = []
    lines.append(f"Summary: {result.total_input} lines in {len(result)} block(s)")
    lines.append("")
    for block in result.blocks:
        lines.append(f"[{block.label}]  count={block.count}")
        if block.first_timestamp:
            lines.append(f"  time : {block.first_timestamp} -> {block.last_timestamp}")
        lines.append(f"  first: {block.first_message}")
        lines.append(f"  last : {block.last_message}")
        if block.sample_lines:
            lines.append("  samples:")
            for sl in block.sample_lines:
                ts = sl.timestamp.isoformat() if sl.timestamp else "no-ts"
                lines.append(f"    [{ts}] {sl.message}")
    return "\n".join(lines)

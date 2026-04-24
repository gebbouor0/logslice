"""fencer.py — extract lines between start/end fence patterns."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional, Pattern

from logslice.parser import LogLine


@dataclass
class FencedBlock:
    lines: List[LogLine] = field(default_factory=list)
    start_index: int = 0
    end_index: Optional[int] = None

    def __len__(self) -> int:
        return len(self.lines)

    @property
    def is_closed(self) -> bool:
        return self.end_index is not None


@dataclass
class FenceResult:
    blocks: List[FencedBlock] = field(default_factory=list)
    total_input: int = 0

    def __len__(self) -> int:
        return len(self.blocks)

    @property
    def total_captured(self) -> int:
        return sum(len(b) for b in self.blocks)


def fence_lines(
    lines: List[LogLine],
    start_pattern: str,
    end_pattern: str,
    include_fences: bool = True,
) -> FenceResult:
    """Extract blocks of lines between start and end fence patterns."""
    start_re: Pattern = re.compile(start_pattern)
    end_re: Pattern = re.compile(end_pattern)

    result = FenceResult(total_input=len(lines))
    current: Optional[FencedBlock] = None

    for line in lines:
        msg = line.message or ""
        if current is None:
            if start_re.search(msg):
                current = FencedBlock(start_index=line.line_number)
                if include_fences:
                    current.lines.append(line)
        else:
            if end_re.search(msg):
                if include_fences:
                    current.lines.append(line)
                current.end_index = line.line_number
                result.blocks.append(current)
                current = None
            else:
                current.lines.append(line)

    # unclosed block
    if current is not None:
        result.blocks.append(current)

    return result


def format_fenced(result: FenceResult) -> str:
    """Render fenced blocks as a human-readable string."""
    if not result.blocks:
        return "(no fenced blocks found)"
    parts: List[str] = []
    for i, block in enumerate(result.blocks, 1):
        closed = "closed" if block.is_closed else "unclosed"
        header = f"[block {i} | lines={len(block)} | {closed}]"
        body = "\n".join(f"  {ln.message}" for ln in block.lines)
        parts.append(f"{header}\n{body}" if body else header)
    return "\n".join(parts)

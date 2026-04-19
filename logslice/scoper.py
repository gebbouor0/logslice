"""Scope log lines to a surrounding window around matched lines."""
from dataclasses import dataclass, field
from typing import List, Optional, Callable
from logslice.parser import LogLine


@dataclass
class ScopedBlock:
    anchor: LogLine
    lines: List[LogLine] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.lines)


def scope_lines(
    lines: List[LogLine],
    match: Callable[[LogLine], bool],
    before: int = 2,
    after: int = 2,
) -> List[ScopedBlock]:
    """Return ScopedBlocks centered on each matching line."""
    if before < 0 or after < 0:
        raise ValueError("before and after must be non-negative")
    blocks: List[ScopedBlock] = []
    n = len(lines)
    covered = set()
    for i, line in enumerate(lines):
        if not match(line):
            continue
        start = max(0, i - before)
        end = min(n - 1, i + after)
        block_lines = lines[start: end + 1]
        block = ScopedBlock(anchor=line, lines=block_lines)
        blocks.append(block)
        covered.update(range(start, end + 1))
    return blocks


def format_scoped(blocks: List[ScopedBlock], separator: str = "---") -> List[str]:
    """Format scoped blocks into human-readable lines."""
    output: List[str] = []
    for idx, block in enumerate(blocks):
        if idx > 0:
            output.append(separator)
        for line in block.lines:
            marker = ">> " if line is block.anchor else "   "
            output.append(f"{marker}[{line.line_number}] {line.message}")
    return output

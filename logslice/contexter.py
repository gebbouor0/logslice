"""Context extraction: grab N lines before/after matching lines."""
from dataclasses import dataclass, field
from typing import List, Optional
from logslice.parser import LogLine


@dataclass
class ContextBlock:
    match: LogLine
    before: List[LogLine] = field(default_factory=list)
    after: List[LogLine] = field(default_factory=list)

    def all_lines(self) -> List[LogLine]:
        seen = set()
        result = []
        for line in self.before + [self.match] + self.after:
            if line.line_number not in seen:
                seen.add(line.line_number)
                result.append(line)
        return sorted(result, key=lambda l: l.line_number)


def extract_context(
    lines: List[LogLine],
    predicate,
    before: int = 2,
    after: int = 2,
) -> List[ContextBlock]:
    """Return ContextBlock for each line matching predicate."""
    if before < 0 or after < 0:
        raise ValueError("before and after must be non-negative")
    blocks = []
    for i, line in enumerate(lines):
        if predicate(line):
            ctx_before = lines[max(0, i - before):i]
            ctx_after = lines[i + 1:i + 1 + after]
            blocks.append(ContextBlock(match=line, before=list(ctx_before), after=list(ctx_after)))
    return blocks


def format_context_blocks(blocks: List[ContextBlock], separator: str = "---") -> List[str]:
    """Render context blocks as text lines."""
    output = []
    for idx, block in enumerate(blocks):
        if idx > 0:
            output.append(separator)
        for line in block.all_lines():
            marker = ">> " if line.line_number == block.match.line_number else "   "
            output.append(f"{marker}[{line.line_number}] {line.message}")
    return output

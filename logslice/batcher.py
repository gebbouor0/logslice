from dataclasses import dataclass, field
from typing import List, Iterator
from logslice.parser import LogLine


@dataclass
class Batch:
    index: int
    lines: List[LogLine] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.lines)

    @property
    def first(self) -> LogLine | None:
        return self.lines[0] if self.lines else None

    @property
    def last(self) -> LogLine | None:
        return self.lines[-1] if self.lines else None


def batch_lines(lines: List[LogLine], batch_size: int) -> List[Batch]:
    if batch_size < 1:
        raise ValueError("batch_size must be >= 1")
    batches = []
    for i in range(0, len(lines), batch_size):
        chunk = lines[i:i + batch_size]
        batches.append(Batch(index=len(batches), lines=chunk))
    return batches


def iter_batches(lines: List[LogLine], batch_size: int) -> Iterator[Batch]:
    for batch in batch_lines(lines, batch_size):
        yield batch


def format_batch(batch: Batch) -> str:
    lines = [f"--- Batch {batch.index} ({len(batch)} lines) ---"]
    for line in batch.lines:
        lines.append(line.raw)
    return "\n".join(lines)

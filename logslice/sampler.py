"""Log line sampling — take every Nth line or a random sample."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import List, Optional

from logslice.parser import LogLine


@dataclass
class SampleResult:
    lines: List[LogLine]
    total_input: int
    sample_size: int
    strategy: str
    seed: Optional[int] = None


def sample_every_nth(lines: List[LogLine], n: int) -> SampleResult:
    """Return every Nth line (1-indexed)."""
    if n < 1:
        raise ValueError(f"n must be >= 1, got {n}")
    sampled = [line for i, line in enumerate(lines) if i % n == 0]
    return SampleResult(
        lines=sampled,
        total_input=len(lines),
        sample_size=len(sampled),
        strategy=f"every_nth:{n}",
    )


def sample_random(
    lines: List[LogLine], count: int, seed: Optional[int] = None
) -> SampleResult:
    """Return a random sample of *count* lines (without replacement)."""
    if count < 0:
        raise ValueError(f"count must be >= 0, got {count}")
    rng = random.Random(seed)
    count = min(count, len(lines))
    sampled = rng.sample(lines, count)
    # preserve original order
    sampled.sort(key=lambda l: l.line_number)
    return SampleResult(
        lines=sampled,
        total_input=len(lines),
        sample_size=len(sampled),
        strategy="random",
        seed=seed,
    )


def sample_lines(
    lines: List[LogLine],
    *,
    every_nth: Optional[int] = None,
    count: Optional[int] = None,
    seed: Optional[int] = None,
) -> SampleResult:
    """Unified entry point — pick one strategy."""
    if every_nth is not None and count is not None:
        raise ValueError("Specify only one of every_nth or count, not both.")
    if every_nth is not None:
        return sample_every_nth(lines, every_nth)
    if count is not None:
        return sample_random(lines, count, seed=seed)
    raise ValueError("Specify either every_nth or count.")

"""Clamp log lines to a maximum count from head or tail."""
from dataclasses import dataclass, field
from typing import List, Literal
from logslice.parser import LogLine


@dataclass
class ClampResult:
    lines: List[LogLine]
    total_input: int
    mode: Literal["head", "tail"]
    limit: int

    @property
    def dropped(self) -> int:
        return self.total_input - len(self.lines)

    def __len__(self) -> int:
        return len(self.lines)


def clamp_head(lines: List[LogLine], limit: int) -> ClampResult:
    """Keep only the first *limit* lines."""
    if limit < 0:
        raise ValueError("limit must be >= 0")
    kept = lines[:limit]
    return ClampResult(lines=kept, total_input=len(lines), mode="head", limit=limit)


def clamp_tail(lines: List[LogLine], limit: int) -> ClampResult:
    """Keep only the last *limit* lines."""
    if limit < 0:
        raise ValueError("limit must be >= 0")
    kept = lines[-limit:] if limit > 0 else []
    return ClampResult(lines=kept, total_input=len(lines), mode="tail", limit=limit)


def clamp_lines(
    lines: List[LogLine],
    limit: int,
    mode: Literal["head", "tail"] = "head",
) -> ClampResult:
    """Dispatch to head or tail clamping."""
    if mode == "head":
        return clamp_head(lines, limit)
    elif mode == "tail":
        return clamp_tail(lines, limit)
    else:
        raise ValueError(f"Unknown mode: {mode!r}")


def format_clamp(result: ClampResult) -> str:
    """Return a summary string for the clamp operation."""
    lines = [line.raw for line in result.lines]
    summary = (
        f"# clamped ({result.mode}, limit={result.limit}, "
        f"kept={len(result)}, dropped={result.dropped})"
    )
    return "\n".join([summary] + lines)

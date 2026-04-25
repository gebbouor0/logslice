"""Assign numeric weights to log lines based on pattern matches."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Iterable, List, Optional

from logslice.parser import LogLine


@dataclass
class WeightedLine:
    _line: LogLine
    weight: float

    @property
    def raw(self) -> str:
        return self._line.raw

    @property
    def line_number(self) -> int:
        return self._line.line_number

    @property
    def message(self) -> str:
        return self._line.message


@dataclass
class WeightRule:
    predicate: Callable[[LogLine], bool]
    weight: float
    label: str = ""


@dataclass
class WeighResult:
    lines: List[WeightedLine] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.lines)

    def top(self, n: int = 10) -> List[WeightedLine]:
        return sorted(self.lines, key=lambda l: l.weight, reverse=True)[:n]

    def bottom(self, n: int = 10) -> List[WeightedLine]:
        return sorted(self.lines, key=lambda l: l.weight)[:n]

    def above(self, threshold: float) -> List[WeightedLine]:
        return [l for l in self.lines if l.weight >= threshold]


def weigh_lines(
    lines: Iterable[LogLine],
    rules: List[WeightRule],
    default_weight: float = 0.0,
) -> WeighResult:
    """Apply weight rules to each line; weights from matching rules are summed."""
    result = WeighResult()
    for line in lines:
        total = default_weight
        for rule in rules:
            if rule.predicate(line):
                total += rule.weight
        result.lines.append(WeightedLine(_line=line, weight=total))
    return result


def format_weighed(result: WeighResult, top_n: Optional[int] = None) -> List[str]:
    """Return formatted strings for weighted lines, optionally limited to top N."""
    lines = result.top(top_n) if top_n is not None else result.lines
    out = []
    for wl in lines:
        out.append(f"[{wl.weight:+.1f}] #{wl.line_number}: {wl.message}")
    return out

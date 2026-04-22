"""Dispatch log lines to named queues based on routing rules."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from logslice.parser import LogLine


@dataclass
class DispatchRule:
    queue: str
    predicate: Callable[[LogLine], bool]
    stop_on_match: bool = True


@dataclass
class DispatchResult:
    queues: Dict[str, List[LogLine]] = field(default_factory=dict)
    unmatched: List[LogLine] = field(default_factory=list)

    def __len__(self) -> int:
        return sum(len(v) for v in self.queues.values()) + len(self.unmatched)

    def get(self, queue: str) -> List[LogLine]:
        return self.queues.get(queue, [])

    @property
    def queue_names(self) -> List[str]:
        return list(self.queues.keys())


def dispatch_lines(
    lines: List[LogLine],
    rules: List[DispatchRule],
    default_queue: Optional[str] = None,
) -> DispatchResult:
    """Route each line to the first matching queue; unmatched go to default_queue or unmatched."""
    result = DispatchResult()

    for line in lines:
        matched = False
        for rule in rules:
            if rule.predicate(line):
                result.queues.setdefault(rule.queue, []).append(line)
                matched = True
                if rule.stop_on_match:
                    break
        if not matched:
            if default_queue is not None:
                result.queues.setdefault(default_queue, []).append(line)
            else:
                result.unmatched.append(line)

    return result


def format_dispatch_summary(result: DispatchResult) -> str:
    """Return a human-readable summary of queue sizes."""
    lines = []
    for name in sorted(result.queue_names):
        lines.append(f"  {name}: {len(result.get(name))} line(s)")
    if result.unmatched:
        lines.append(f"  <unmatched>: {len(result.unmatched)} line(s)")
    if not lines:
        return "No lines dispatched."
    return "Dispatch summary:\n" + "\n".join(lines)

"""Partition log lines into named segments based on field value or pattern."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional
import re
from logslice.parser import LogLine


@dataclass
class Partition:
    name: str
    lines: List[LogLine] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.lines)


@dataclass
class PartitionResult:
    partitions: Dict[str, Partition] = field(default_factory=dict)
    unmatched: List[LogLine] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.partitions)

    @property
    def total_lines(self) -> int:
        return sum(len(p) for p in self.partitions.values()) + len(self.unmatched)

    def get(self, name: str) -> Optional[Partition]:
        return self.partitions.get(name)


def _extract_level(message: str) -> str:
    m = re.search(r'\b(DEBUG|INFO|WARNING|ERROR|CRITICAL)\b', message, re.IGNORECASE)
    return m.group(1).upper() if m else "UNKNOWN"


def partition_by_pattern(
    lines: List[LogLine],
    rules: Dict[str, str],
    default_partition: Optional[str] = None,
) -> PartitionResult:
    """Assign each line to the first matching named regex rule."""
    compiled = {name: re.compile(pat) for name, pat in rules.items()}
    result = PartitionResult()

    for line in lines:
        matched = False
        for name, rx in compiled.items():
            if rx.search(line.message):
                if name not in result.partitions:
                    result.partitions[name] = Partition(name=name)
                result.partitions[name].lines.append(line)
                matched = True
                break
        if not matched:
            if default_partition is not None:
                if default_partition not in result.partitions:
                    result.partitions[default_partition] = Partition(name=default_partition)
                result.partitions[default_partition].lines.append(line)
            else:
                result.unmatched.append(line)

    return result


def partition_by_field(
    lines: List[LogLine],
    field_fn: Callable[[LogLine], str],
) -> PartitionResult:
    """Partition lines by an arbitrary field extractor function."""
    result = PartitionResult()
    for line in lines:
        key = field_fn(line)
        if key not in result.partitions:
            result.partitions[key] = Partition(name=key)
        result.partitions[key].lines.append(line)
    return result


def partition_by_level(lines: List[LogLine]) -> PartitionResult:
    """Convenience wrapper: partition by detected log level."""
    return partition_by_field(lines, lambda ln: _extract_level(ln.message))


def format_partitions(result: PartitionResult) -> str:
    parts = []
    for name, partition in sorted(result.partitions.items()):
        parts.append(f"[{name}] {len(partition)} line(s)")
    if result.unmatched:
        parts.append(f"[unmatched] {len(result.unmatched)} line(s)")
    return "\n".join(parts)

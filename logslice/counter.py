from dataclasses import dataclass, field
from typing import List, Dict, Optional
from collections import Counter
from logslice.parser import LogLine


@dataclass
class CountResult:
    total: int
    by_field: Dict[str, int]
    field_name: str

    def top(self, n: int = 5) -> List[tuple]:
        return sorted(self.by_field.items(), key=lambda x: x[1], reverse=True)[:n]

    def least(self, n: int = 5) -> List[tuple]:
        return sorted(self.by_field.items(), key=lambda x: x[1])[:n]


def count_by_pattern(lines: List[LogLine], pattern: str) -> int:
    import re
    rx = re.compile(pattern)
    return sum(1 for ln in lines if rx.search(ln.message))


def count_by_field(lines: List[LogLine], field_name: str) -> CountResult:
    values: List[str] = []
    for ln in lines:
        val = getattr(ln, field_name, None)
        if val is None:
            val = "<none>"
        values.append(str(val))
    counts = dict(Counter(values))
    return CountResult(total=len(lines), by_field=counts, field_name=field_name)


def count_by_hour(lines: List[LogLine]) -> CountResult:
    buckets: List[str] = []
    for ln in lines:
        if ln.timestamp:
            buckets.append(ln.timestamp.strftime("%Y-%m-%d %H:00"))
        else:
            buckets.append("<no timestamp>")
    counts = dict(Counter(buckets))
    return CountResult(total=len(lines), by_field=counts, field_name="hour")


def format_count_result(result: CountResult, top_n: int = 0) -> str:
    lines = [f"Total lines: {result.total}", f"Breakdown by {result.field_name}:"]
    items = result.top(top_n) if top_n > 0 else sorted(result.by_field.items())
    for key, val in items:
        lines.append(f"  {key}: {val}")
    return "\n".join(lines)

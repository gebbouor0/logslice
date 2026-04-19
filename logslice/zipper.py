"""Zip two log streams side-by-side by line index or timestamp."""
from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from logslice.parser import LogLine


@dataclass
class ZippedRow:
    index: int
    left: Optional[LogLine]
    right: Optional[LogLine]

    @property
    def left_message(self) -> str:
        return self.left.message if self.left else ""

    @property
    def right_message(self) -> str:
        return self.right.message if self.right else ""


def zip_by_index(left: List[LogLine], right: List[LogLine]) -> List[ZippedRow]:
    """Pair lines by position; shorter stream gets None-padded."""
    length = max(len(left), len(right))
    rows = []
    for i in range(length):
        l = left[i] if i < len(left) else None
        r = right[i] if i < len(right) else None
        rows.append(ZippedRow(index=i, left=l, right=r))
    return rows


def zip_by_timestamp(left: List[LogLine], right: List[LogLine]) -> List[ZippedRow]:
    """Align lines by nearest timestamp; unmatched lines get None partner."""
    timed_left = [l for l in left if l.timestamp]
    timed_right = [r for r in right if r.timestamp]
    used_right = set()
    rows = []
    for i, l in enumerate(timed_left):
        best = None
        best_delta = None
        for j, r in enumerate(timed_right):
            if j in used_right:
                continue
            delta = abs((r.timestamp - l.timestamp).total_seconds())
            if best_delta is None or delta < best_delta:
                best_delta = delta
                best = (j, r)
        if best:
            used_right.add(best[0])
            rows.append(ZippedRow(index=i, left=l, right=best[1]))
        else:
            rows.append(ZippedRow(index=i, left=l, right=None))
    for j, r in enumerate(timed_right):
        if j not in used_right:
            rows.append(ZippedRow(index=len(rows), left=None, right=r))
    return rows


def format_zipped(rows: List[ZippedRow], width: int = 40) -> List[str]:
    lines = []
    header = f"{'LEFT':<{width}} | {'RIGHT':<{width}}"
    lines.append(header)
    lines.append("-" * (width * 2 + 3))
    for row in rows:
        l = row.left_message[:width].ljust(width)
        r = row.right_message[:width].ljust(width)
        lines.append(f"{l} | {r}")
    return lines

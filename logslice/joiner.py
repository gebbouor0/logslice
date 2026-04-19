"""Join log lines from two streams by a shared field value."""
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from logslice.parser import LogLine


@dataclass
class JoinedRow:
    key: str
    left: Optional[LogLine]
    right: Optional[LogLine]

    @property
    def left_message(self) -> str:
        return self.left.message if self.left else ""

    @property
    def right_message(self) -> str:
        return self.right.message if self.right else ""


def _extract_field(line: LogLine, field_name: str) -> Optional[str]:
    if field_name == "message":
        return line.message
    if field_name == "level":
        import re
        m = re.search(r"\b(DEBUG|INFO|WARNING|ERROR|CRITICAL)\b", line.message, re.IGNORECASE)
        return m.group(1).upper() if m else None
    return None


def join_streams(
    left: List[LogLine],
    right: List[LogLine],
    field_name: str = "level",
    how: str = "inner",
) -> List[JoinedRow]:
    """Join two log streams on a shared field. how: inner | left | right | outer."""
    left_map: Dict[str, List[LogLine]] = {}
    for line in left:
        k = _extract_field(line, field_name)
        if k is not None:
            left_map.setdefault(k, []).append(line)

    right_map: Dict[str, List[LogLine]] = {}
    for line in right:
        k = _extract_field(line, field_name)
        if k is not None:
            right_map.setdefault(k, []).append(line)

    all_keys = set()
    if how in ("inner", "left"):
        all_keys = set(left_map.keys())
    if how == "right":
        all_keys = set(right_map.keys())
    if how in ("outer", "left"):
        all_keys = set(left_map.keys())
    if how == "outer":
        all_keys |= set(right_map.keys())
    if how == "inner":
        all_keys &= set(right_map.keys())

    rows: List[JoinedRow] = []
    for key in sorted(all_keys):
        lefts = left_map.get(key, [None])
        rights = right_map.get(key, [None])
        for l in lefts:
            for r in rights:
                rows.append(JoinedRow(key=key, left=l, right=r))
    return rows


def format_joined(rows: List[JoinedRow]) -> List[str]:
    out = []
    for row in rows:
        out.append(f"[{row.key}] LEFT={row.left_message!r} RIGHT={row.right_message!r}")
    return out

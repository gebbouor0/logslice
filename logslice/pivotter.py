"""Pivot log lines by a field, grouping messages under each unique field value."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from logslice.parser import LogLine


@dataclass
class PivotTable:
    field_name: str
    groups: Dict[str, List[LogLine]] = field(default_factory=dict)

    def keys(self) -> List[str]:
        return sorted(self.groups.keys())

    def __len__(self) -> int:
        return len(self.groups)


def _extract_field(line: LogLine, field_name: str) -> Optional[str]:
    if field_name == "level":
        msg = line.message.upper()
        for lvl in ("ERROR", "WARN", "INFO", "DEBUG"):
            if lvl in msg:
                return lvl
        return None
    if field_name == "hour" and line.timestamp is not None:
        return line.timestamp.strftime("%Y-%m-%d %H:00")
    return None


def pivot_lines(
    lines: List[LogLine],
    field_name: str,
    default_key: str = "OTHER",
) -> PivotTable:
    table = PivotTable(field_name=field_name)
    for line in lines:
        key = _extract_field(line, field_name) or default_key
        table.groups.setdefault(key, []).append(line)
    return table


def format_pivot(table: PivotTable, max_per_group: int = 5) -> str:
    lines = [f"Pivot by '{table.field_name}':"]
    for key in table.keys():
        entries = table.groups[key]
        lines.append(f"  [{key}] ({len(entries)} lines)")
        for entry in entries[:max_per_group]:
            lines.append(f"    {entry.message}")
        if len(entries) > max_per_group:
            lines.append(f"    ... and {len(entries) - max_per_group} more")
    return "\n".join(lines)

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable
from logslice.parser import LogLine


@dataclass
class Group:
    key: str
    lines: List[LogLine] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.lines)


def group_by_field(lines: List[LogLine], key_fn: Callable[[LogLine], Optional[str]], default: str = "(none)") -> Dict[str, Group]:
    groups: Dict[str, Group] = {}
    for line in lines:
        key = key_fn(line) or default
        if key not in groups:
            groups[key] = Group(key=key)
        groups[key].lines.append(line)
    return groups


def group_by_level(lines: List[LogLine]) -> Dict[str, Group]:
    import re
    level_re = re.compile(r'\b(DEBUG|INFO|WARNING|WARN|ERROR|CRITICAL)\b', re.IGNORECASE)

    def extract_level(line: LogLine) -> Optional[str]:
        m = level_re.search(line.message)
        return m.group(1).upper() if m else None

    return group_by_field(lines, extract_level, default="UNKNOWN")


def group_by_hour(lines: List[LogLine]) -> Dict[str, Group]:
    def extract_hour(line: LogLine) -> Optional[str]:
        if line.timestamp is None:
            return None
        return line.timestamp.strftime("%Y-%m-%d %H:00")

    return group_by_field(lines, extract_hour, default="(no timestamp)")


def format_groups(groups: Dict[str, Group]) -> str:
    parts = []
    for key, group in sorted(groups.items()):
        parts.append(f"[{key}] ({len(group)} lines)")
        for line in group.lines:
            parts.append(f"  {line.message}")
    return "\n".join(parts)

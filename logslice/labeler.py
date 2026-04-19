from dataclasses import dataclass, field
from typing import List, Dict, Optional
from logslice.parser import LogLine


@dataclass
class LabeledLine:
    log_line: LogLine
    labels: Dict[str, str] = field(default_factory=dict)

    @property
    def raw(self) -> str:
        return self.log_line.raw

    @property
    def line_number(self) -> Optional[int]:
        return self.log_line.line_number


def label_line(log_line: LogLine, rules: Dict[str, str]) -> LabeledLine:
    """Apply label rules to a log line. Rules map label_key -> regex pattern."""
    import re
    labels = {}
    for key, pattern in rules.items():
        if re.search(pattern, log_line.message):
            labels[key] = pattern
    return LabeledLine(log_line=log_line, labels=labels)


def label_lines(log_lines: List[LogLine], rules: Dict[str, str]) -> List[LabeledLine]:
    """Apply label rules to a list of log lines."""
    return [label_line(line, rules) for line in log_lines]


def format_labeled(labeled: LabeledLine, separator: str = " | ") -> str:
    """Format a labeled line for display."""
    label_str = ", ".join(f"{k}" for k in labeled.labels) if labeled.labels else "(none)"
    return f"[{label_str}]{separator}{labeled.raw}"


def group_by_label(labeled_lines: List[LabeledLine]) -> Dict[str, List[LabeledLine]]:
    """Group labeled lines by their label keys."""
    groups: Dict[str, List[LabeledLine]] = {}
    for ll in labeled_lines:
        if not ll.labels:
            groups.setdefault("unlabeled", []).append(ll)
        for key in ll.labels:
            groups.setdefault(key, []).append(ll)
    return groups

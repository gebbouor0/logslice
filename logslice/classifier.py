from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re

from logslice.parser import LogLine


@dataclass
class ClassifiedLine:
    log_line: LogLine
    category: str
    matched_rule: Optional[str] = None

    @property
    def raw(self) -> str:
        return self.log_line.raw

    @property
    def line_number(self) -> int:
        return self.log_line.line_number


@dataclass
class ClassifyResult:
    categories: Dict[str, List[ClassifiedLine]] = field(default_factory=dict)

    def add(self, line: ClassifiedLine) -> None:
        self.categories.setdefault(line.category, []).append(line)

    def all_lines(self) -> List[ClassifiedLine]:
        out = []
        for lines in self.categories.values():
            out.extend(lines)
        return sorted(out, key=lambda l: l.line_number)


def classify_lines(
    lines: List[LogLine],
    rules: Dict[str, str],
    default_category: str = "uncategorized",
    case_sensitive: bool = False,
) -> ClassifyResult:
    """Classify log lines into categories based on regex rules.

    Args:
        lines: Parsed log lines.
        rules: Mapping of category name -> regex pattern.
        default_category: Category assigned when no rule matches.
        case_sensitive: Whether pattern matching is case-sensitive.
    """
    flags = 0 if case_sensitive else re.IGNORECASE
    compiled = {name: re.compile(pat, flags) for name, pat in rules.items()}
    result = ClassifyResult()
    for line in lines:
        matched_cat = default_category
        matched_rule = None
        for name, pattern in compiled.items():
            if pattern.search(line.message):
                matched_cat = name
                matched_rule = name
                break
        result.add(ClassifiedLine(log_line=line, category=matched_cat, matched_rule=matched_rule))
    return result

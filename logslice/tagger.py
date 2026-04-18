from dataclasses import dataclass, field
from typing import List, Optional
import re
from logslice.parser import LogLine


@dataclass
class TaggedLine:
    log_line: LogLine
    tags: List[str] = field(default_factory=list)

    @property
    def raw(self) -> str:
        return self.log_line.raw

    @property
    def line_number(self) -> Optional[int]:
        return self.log_line.line_number


def tag_line(log_line: LogLine, rules: dict[str, str]) -> TaggedLine:
    """Apply tag rules (tag -> pattern) to a single log line."""
    tags = []
    for tag, pattern in rules.items():
        if re.search(pattern, log_line.raw):
            tags.append(tag)
    return TaggedLine(log_line=log_line, tags=tags)


def tag_lines(log_lines: List[LogLine], rules: dict[str, str]) -> List[TaggedLine]:
    """Tag all lines using the provided rules."""
    return [tag_line(line, rules) for line in log_lines]


def filter_by_tag(tagged_lines: List[TaggedLine], tag: str) -> List[TaggedLine]:
    """Return only lines that have the given tag."""
    return [tl for tl in tagged_lines if tag in tl.tags]


def format_tagged(tagged_line: TaggedLine) -> str:
    tag_str = "[" + ",".join(sorted(tagged_line.tags)) + "]" if tagged_line.tags else "[]"
    return f"{tag_str} {tagged_line.raw}"

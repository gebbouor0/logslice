"""Annotate log lines with custom tags or markers."""
from dataclasses import dataclass, field
from typing import Optional
from logslice.parser import LogLine


@dataclass
class AnnotatedLine:
    log_line: LogLine
    tags: list[str] = field(default_factory=list)
    note: Optional[str] = None

    @property
    def raw(self) -> str:
        return self.log_line.raw

    @property
    def line_number(self) -> int:
        return self.log_line.line_number


def annotate_lines(
    lines: list[LogLine],
    tag_rules: dict[str, str],
    note_pattern: Optional[str] = None,
) -> list[AnnotatedLine]:
    """Tag lines whose raw text matches each rule's pattern.

    tag_rules: mapping of tag name -> substring pattern
    note_pattern: if set, lines matching it get a generic note
    """
    import re

    annotated = []
    note_re = re.compile(note_pattern) if note_pattern else None

    for line in lines:
        tags = [
            tag for tag, pattern in tag_rules.items() if pattern in line.raw
        ]
        note = None
        if note_re and note_re.search(line.raw):
            note = f"matches: {note_pattern}"
        annotated.append(AnnotatedLine(log_line=line, tags=tags, note=note))

    return annotated


def format_annotated(lines: list[AnnotatedLine], show_tags: bool = True) -> list[str]:
    """Render annotated lines as strings."""
    out = []
    for al in lines:
        prefix = ""
        if show_tags and al.tags:
            prefix = "[" + ",".join(al.tags) + "] "
        suffix = f"  # {al.note}" if al.note else ""
        out.append(f"{prefix}{al.raw}{suffix}")
    return out

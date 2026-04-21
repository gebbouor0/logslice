"""extract structured fields from log message text via named-group patterns"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re

from logslice.parser import LogLine


@dataclass
class ExtractedLine:
    _line: LogLine
    fields: Dict[str, str] = field(default_factory=dict)

    @property
    def raw(self) -> str:
        return self._line.raw

    @property
    def line_number(self) -> int:
        return self._line.line_number

    @property
    def message(self) -> str:
        return self._line.message


@dataclass
class ExtractResult:
    lines: List[ExtractedLine] = field(default_factory=list)
    pattern: str = ""

    def __len__(self) -> int:
        return len(self.lines)

    @property
    def matched(self) -> List[ExtractedLine]:
        return [l for l in self.lines if l.fields]

    @property
    def unmatched(self) -> List[ExtractedLine]:
        return [l for l in self.lines if not l.fields]

    def column(self, name: str) -> List[Optional[str]]:
        """Return values for a single field across all lines."""
        return [l.fields.get(name) for l in self.lines]


def extract_fields(
    lines: List[LogLine],
    pattern: str,
    flags: int = re.IGNORECASE,
) -> ExtractResult:
    """Apply a regex with named groups to each line's message.

    Lines that don't match get an empty fields dict.
    """
    rx = re.compile(pattern, flags)
    result = ExtractResult(pattern=pattern)

    for line in lines:
        m = rx.search(line.message)
        extracted = ExtractedLine(
            _line=line,
            fields=dict(m.groupdict()) if m else {},
        )
        result.lines.append(extracted)

    return result


def format_extracted(result: ExtractResult) -> str:
    rows: List[str] = []
    for el in result.lines:
        if el.fields:
            field_str = "  ".join(f"{k}={v}" for k, v in el.fields.items())
            rows.append(f"[{el.line_number}] {field_str}")
        else:
            rows.append(f"[{el.line_number}] <no match>")
    return "\n".join(rows)

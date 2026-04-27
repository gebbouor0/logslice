"""censor.py — redact or replace tokens in log messages by category."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable, List, Optional

from logslice.parser import LogLine

# Built-in category patterns
_BUILTIN: dict[str, str] = {
    "ip": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
    "email": r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}",
    "uuid": r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
    "token": r"(?i)(?:bearer|token)[\s=:]+\S+",
    "credit_card": r"\b(?:\d[ -]?){13,16}\b",
}


@dataclass
class CensoredLine:
    raw: str
    line_number: int
    message: str
    timestamp: object
    level: Optional[str]
    was_censored: bool
    categories_hit: List[str] = field(default_factory=list)

    def as_log_line(self) -> LogLine:
        ll = LogLine(raw=self.raw, line_number=self.line_number)
        ll.timestamp = self.timestamp
        ll.level = self.level
        ll.message = self.message
        return ll


@dataclass
class CensorResult:
    lines: List[CensoredLine] = field(default_factory=list)
    total_input: int = 0
    total_censored: int = 0

    def __len__(self) -> int:
        return len(self.lines)

    @property
    def censor_rate(self) -> float:
        if self.total_input == 0:
            return 0.0
        return self.total_censored / self.total_input


def censor_lines(
    lines: Iterable[LogLine],
    categories: Optional[List[str]] = None,
    extra_patterns: Optional[dict[str, str]] = None,
    placeholder: str = "[CENSORED]",
) -> CensorResult:
    """Censor tokens in messages by category name or custom pattern."""
    patterns: dict[str, str] = {}
    cats = categories or list(_BUILTIN.keys())
    for cat in cats:
        if cat in _BUILTIN:
            patterns[cat] = _BUILTIN[cat]
    if extra_patterns:
        patterns.update(extra_patterns)

    compiled = {cat: re.compile(pat) for cat, pat in patterns.items()}
    result = CensorResult()

    for line in lines:
        result.total_input += 1
        msg = line.message or ""
        hits: List[str] = []
        for cat, rx in compiled.items():
            new_msg, n = rx.subn(placeholder, msg)
            if n:
                hits.append(cat)
                msg = new_msg
        cl = CensoredLine(
            raw=line.raw,
            line_number=line.line_number,
            message=msg,
            timestamp=line.timestamp,
            level=getattr(line, "level", None),
            was_censored=bool(hits),
            categories_hit=hits,
        )
        result.lines.append(cl)
        if hits:
            result.total_censored += 1

    return result


def format_censor(result: CensorResult) -> List[str]:
    out: List[str] = []
    for cl in result.lines:
        marker = " [*]" if cl.was_censored else ""
        out.append(f"{cl.line_number:>6}: {cl.message}{marker}")
    return out

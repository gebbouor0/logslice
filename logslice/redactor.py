"""Redact sensitive patterns from log lines."""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import List, Optional
from logslice.parser import LogLine


@dataclass
class RedactedLine:
    original: LogLine
    redacted_message: str
    matched_patterns: List[str] = field(default_factory=list)

    @property
    def raw(self) -> str:
        return self.original.raw

    @property
    def line_number(self) -> Optional[int]:
        return self.original.line_number


DEFAULT_PLACEHOLDER = "[REDACTED]"

BUILTIN_PATTERNS = {
    "email": r"[\w.+-]+@[\w-]+\.[\w.]+",
    "ip": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
    "token": r"(?i)(?:token|key|secret|password)=[^\s&]+",
    "uuid": r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
}


def redact_message(
    message: str,
    patterns: List[str],
    placeholder: str = DEFAULT_PLACEHOLDER,
) -> tuple[str, List[str]]:
    matched: List[str] = []
    result = message
    for pat in patterns:
        compiled = re.compile(pat)
        if compiled.search(result):
            matched.append(pat)
            result = compiled.sub(placeholder, result)
    return result, matched


def redact_line(
    line: LogLine,
    patterns: List[str],
    placeholder: str = DEFAULT_PLACEHOLDER,
) -> RedactedLine:
    redacted, matched = redact_message(line.message, patterns, placeholder)
    return RedactedLine(original=line, redacted_message=redacted, matched_patterns=matched)


def redact_lines(
    lines: List[LogLine],
    patterns: List[str],
    placeholder: str = DEFAULT_PLACEHOLDER,
    builtins: Optional[List[str]] = None,
) -> List[RedactedLine]:
    all_patterns = list(patterns)
    for name in (builtins or []):
        if name in BUILTIN_PATTERNS:
            all_patterns.append(BUILTIN_PATTERNS[name])
    return [redact_line(l, all_patterns, placeholder) for l in lines]

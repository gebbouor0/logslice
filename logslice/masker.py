"""Mask sensitive fields in log messages using named patterns."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from logslice.parser import LogLine


# Built-in named patterns for common sensitive data
BUILTIN_PATTERNS: Dict[str, str] = {
    "ip": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
    "email": r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}",
    "token": r"(?i)(?:token|key|secret|password)=[^\s&]+",
    "uuid": r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
    "credit_card": r"\b(?:\d[ -]?){13,16}\b",
}


@dataclass
class MaskedLine:
    _log_line: LogLine
    masked_message: str
    applied_masks: List[str] = field(default_factory=list)

    @property
    def raw(self) -> str:
        return self._log_line.raw

    @property
    def line_number(self) -> Optional[int]:
        return self._log_line.line_number


def mask_message(
    message: str,
    patterns: Dict[str, str],
    placeholder: str = "[MASKED]",
) -> tuple[str, List[str]]:
    """Apply named patterns to message, returning (masked_text, list_of_applied_names)."""
    result = message
    applied: List[str] = []
    for name, pattern in patterns.items():
        new_result, count = re.subn(pattern, placeholder, result)
        if count > 0:
            result = new_result
            applied.append(name)
    return result, applied


def mask_line(
    log_line: LogLine,
    patterns: Dict[str, str],
    placeholder: str = "[MASKED]",
) -> MaskedLine:
    """Mask a single LogLine."""
    msg = log_line.message or ""
    masked, applied = mask_message(msg, patterns, placeholder)
    return MaskedLine(
        _log_line=log_line,
        masked_message=masked,
        applied_masks=applied,
    )


def mask_lines(
    lines: List[LogLine],
    patterns: Optional[Dict[str, str]] = None,
    use_builtins: bool = True,
    extra_patterns: Optional[Dict[str, str]] = None,
    placeholder: str = "[MASKED]",
) -> List[MaskedLine]:
    """Mask a list of LogLines using built-in and/or custom patterns."""
    combined: Dict[str, str] = {}
    if use_builtins:
        combined.update(BUILTIN_PATTERNS)
    if patterns:
        combined.update(patterns)
    if extra_patterns:
        combined.update(extra_patterns)
    return [mask_line(line, combined, placeholder) for line in lines]

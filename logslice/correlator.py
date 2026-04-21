"""correlator.py — find lines across two streams that share a common field or pattern."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable, List, Optional, Tuple

from logslice.parser import LogLine


@dataclass
class CorrelatedPair:
    """A matched pair of log lines from two separate streams."""

    left: LogLine
    right: LogLine
    key: str  # the value that caused the match

    @property
    def left_message(self) -> str:
        return self.left.message

    @property
    def right_message(self) -> str:
        return self.right.message


@dataclass
class CorrelateResult:
    """Result of correlating two log streams."""

    pairs: List[CorrelatedPair] = field(default_factory=list)
    unmatched_left: List[LogLine] = field(default_factory=list)
    unmatched_right: List[LogLine] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.pairs)

    @property
    def total_unmatched(self) -> int:
        return len(self.unmatched_left) + len(self.unmatched_right)


def _extract_key_by_pattern(line: LogLine, pattern: str) -> Optional[str]:
    """Return the first capture group from *pattern* applied to line.message."""
    m = re.search(pattern, line.message)
    if m:
        # Use the first group if present, otherwise the whole match
        return m.group(1) if m.lastindex else m.group(0)
    return None


def _extract_key_by_field(line: LogLine, field_name: str) -> Optional[str]:
    """Return a simple field value from a LogLine (message or level)."""
    if field_name == "level":
        return line.level
    if field_name == "message":
        return line.message
    return None


def correlate_by_pattern(
    left: List[LogLine],
    right: List[LogLine],
    pattern: str,
) -> CorrelateResult:
    """Correlate two streams by matching a regex pattern against each line's message.

    Lines from *left* and *right* whose first capture group (or full match)
    of *pattern* are equal form a :class:`CorrelatedPair`.  Each key is matched
    at most once — first-come-first-served within each stream.
    """
    result = CorrelateResult()

    # Build an index of key -> list[LogLine] for the right stream
    right_index: dict[str, list[LogLine]] = {}
    for line in right:
        key = _extract_key_by_pattern(line, pattern)
        if key is not None:
            right_index.setdefault(key, []).append(line)

    used_right: set[int] = set()  # track by id() to avoid double-matching

    for line in left:
        key = _extract_key_by_pattern(line, pattern)
        if key is None:
            result.unmatched_left.append(line)
            continue

        candidates = right_index.get(key, [])
        matched = False
        for candidate in candidates:
            if id(candidate) not in used_right:
                used_right.add(id(candidate))
                result.pairs.append(CorrelatedPair(left=line, right=candidate, key=key))
                matched = True
                break

        if not matched:
            result.unmatched_left.append(line)

    # Any right lines never used are unmatched
    for line in right:
        if id(line) not in used_right:
            key = _extract_key_by_pattern(line, pattern)
            if key is not None or True:  # include all unmatched right lines
                result.unmatched_right.append(line)

    return result


def correlate_by_field(
    left: List[LogLine],
    right: List[LogLine],
    field_name: str,
) -> CorrelateResult:
    """Correlate two streams by matching a named field (e.g. 'level')."""
    result = CorrelateResult()

    right_index: dict[str, list[LogLine]] = {}
    for line in right:
        key = _extract_key_by_field(line, field_name)
        if key is not None:
            right_index.setdefault(key, []).append(line)

    used_right: set[int] = set()

    for line in left:
        key = _extract_key_by_field(line, field_name)
        if key is None:
            result.unmatched_left.append(line)
            continue

        candidates = right_index.get(key, [])
        matched = False
        for candidate in candidates:
            if id(candidate) not in used_right:
                used_right.add(id(candidate))
                result.pairs.append(CorrelatedPair(left=line, right=candidate, key=key))
                matched = True
                break

        if not matched:
            result.unmatched_left.append(line)

    for line in right:
        if id(line) not in used_right:
            result.unmatched_right.append(line)

    return result


def format_correlated(result: CorrelateResult, separator: str = " <-> ") -> List[str]:
    """Render correlated pairs as human-readable strings."""
    lines: List[str] = []
    for pair in result.pairs:
        lines.append(f"[{pair.key}] {pair.left_message}{separator}{pair.right_message}")
    return lines

"""Validate log lines against structural rules."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Callable, Optional
from logslice.parser import LogLine


@dataclass
class ValidationRule:
    name: str
    check: Callable[[LogLine], bool]
    message: str = "validation failed"


@dataclass
class Violation:
    line: LogLine
    rule_name: str
    message: str


@dataclass
class ValidationResult:
    violations: List[Violation] = field(default_factory=list)
    total: int = 0

    @property
    def valid_count(self) -> int:
        return self.total - len(self.violations)

    @property
    def is_clean(self) -> bool:
        return len(self.violations) == 0


def validate_lines(lines: List[LogLine], rules: List[ValidationRule]) -> ValidationResult:
    result = ValidationResult(total=len(lines))
    for line in lines:
        for rule in rules:
            if not rule.check(line):
                result.violations.append(
                    Violation(line=line, rule_name=rule.name, message=rule.message)
                )
    return result


def format_violations(result: ValidationResult) -> str:
    if result.is_clean:
        return f"All {result.total} lines passed validation."
    parts = [f"{len(result.violations)} violation(s) in {result.total} lines:"]
    for v in result.violations:
        ln = v.line.line_number
        parts.append(f"  line {ln}: [{v.rule_name}] {v.message}")
    return "\n".join(parts)


# Built-in rules
HAS_TIMESTAMP = ValidationRule(
    name="has_timestamp",
    check=lambda l: l.timestamp is not None,
    message="missing timestamp",
)

HAS_LEVEL = ValidationRule(
    name="has_level",
    check=lambda l: bool(l.level),
    message="missing log level",
)

NON_EMPTY_MESSAGE = ValidationRule(
    name="non_empty_message",
    check=lambda l: bool(l.message.strip()),
    message="empty message",
)

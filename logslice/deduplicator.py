"""Deduplication of repeated log lines."""
from dataclasses import dataclass, field
from typing import List, Tuple
from logslice.parser import LogLine


@dataclass
class DeduplicatedLine:
    line: LogLine
    count: int = 1


def deduplicate_lines(lines: List[LogLine]) -> List[DeduplicatedLine]:
    """Collapse consecutive duplicate messages into a single entry with a count."""
    result: List[DeduplicatedLine] = []
    for log_line in lines:
        if result and result[-1].line.message == log_line.message:
            result[-1].count += 1
        else:
            result.append(DeduplicatedLine(line=log_line, count=1))
    return result


def format_deduplicated(deduped: List[DeduplicatedLine]) -> List[str]:
    """Format deduplicated lines for output, appending repeat count when > 1."""
    output = []
    for entry in deduped:
        base = entry.line.raw.rstrip()
        if entry.count > 1:
            output.append(f"{base}  [repeated {entry.count}x]")
        else:
            output.append(base)
    return output


def deduplicate_and_format(lines: List[LogLine]) -> Tuple[List[DeduplicatedLine], List[str]]:
    """Convenience wrapper: deduplicate then format."""
    deduped = deduplicate_lines(lines)
    formatted = format_deduplicated(deduped)
    return deduped, formatted

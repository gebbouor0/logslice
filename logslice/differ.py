"""Diff two streams of log lines, highlighting added/removed entries."""
from dataclasses import dataclass
from typing import List, Optional
from logslice.parser import LogLine


@dataclass
class DiffLine:
    line: LogLine
    status: str  # 'added', 'removed', 'common'

    @property
    def raw(self) -> str:
        return self.line.raw

    @property
    def line_number(self) -> Optional[int]:
        return self.line.line_number


def _messages(lines: List[LogLine]) -> List[str]:
    return [l.raw.strip() for l in lines]


def diff_streams(left: List[LogLine], right: List[LogLine]) -> List[DiffLine]:
    """Return a list of DiffLine entries comparing left vs right."""
    left_msgs = set(_messages(left))
    right_msgs = set(_messages(right))

    result: List[DiffLine] = []

    for line in left:
        msg = line.raw.strip()
        status = "common" if msg in right_msgs else "removed"
        result.append(DiffLine(line=line, status=status))

    for line in right:
        msg = line.raw.strip()
        if msg not in left_msgs:
            result.append(DiffLine(line=line, status="added"))

    return result


STATUS_PREFIX = {
    "added": "+ ",
    "removed": "- ",
    "common": "  ",
}


def format_diff(diff: List[DiffLine], color: bool = False) -> List[str]:
    """Format diff lines with +/- prefixes, optionally with ANSI color."""
    COLOR_MAP = {"added": "\033[32m", "removed": "\033[31m", "common": ""}
    RESET = "\033[0m"
    output = []
    for d in diff:
        prefix = STATUS_PREFIX.get(d.status, "  ")
        text = f"{prefix}{d.raw.rstrip()}"
        if color and d.status in ("added", "removed"):
            text = f"{COLOR_MAP[d.status]}{text}{RESET}"
        output.append(text)
    return output


def diff_and_format(left: List[LogLine], right: List[LogLine], color: bool = False) -> List[str]:
    return format_diff(diff_streams(left, right), color=color)

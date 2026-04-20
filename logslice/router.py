"""Route log lines to different named channels based on pattern rules."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from logslice.parser import LogLine


@dataclass
class RouteRule:
    """A rule that maps a regex pattern to a named channel."""

    channel: str
    pattern: str
    flags: int = re.IGNORECASE

    def __post_init__(self) -> None:
        self._regex = re.compile(self.pattern, self.flags)

    def matches(self, line: LogLine) -> bool:
        return bool(self._regex.search(line.message))


@dataclass
class RoutedLine:
    """A log line that has been assigned to a channel."""

    line: LogLine
    channel: str

    @property
    def raw(self) -> str:
        return self.line.raw

    @property
    def line_number(self) -> Optional[int]:
        return self.line.line_number


@dataclass
class RouteResult:
    """Collection of routed lines grouped by channel."""

    channels: Dict[str, List[RoutedLine]] = field(default_factory=dict)
    unrouted: List[LogLine] = field(default_factory=list)

    def __len__(self) -> int:
        return sum(len(v) for v in self.channels.values()) + len(self.unrouted)

    def channel_names(self) -> List[str]:
        """Return sorted list of channel names that received at least one line."""
        return sorted(self.channels.keys())

    def get(self, channel: str) -> List[RoutedLine]:
        """Return lines routed to *channel*, or empty list if channel is unknown."""
        return self.channels.get(channel, [])


def route_lines(
    lines: List[LogLine],
    rules: List[RouteRule],
    default_channel: Optional[str] = None,
) -> RouteResult:
    """Route each line to the first matching channel.

    Args:
        lines: Parsed log lines to route.
        rules: Ordered list of routing rules; first match wins.
        default_channel: If provided, unmatched lines go here instead of
            ``result.unrouted``.

    Returns:
        A :class:`RouteResult` containing all routed (and optionally
        unrouted) lines.
    """
    result = RouteResult()

    for line in lines:
        matched = False
        for rule in rules:
            if rule.matches(line):
                routed = RoutedLine(line=line, channel=rule.channel)
                result.channels.setdefault(rule.channel, []).append(routed)
                matched = True
                break

        if not matched:
            if default_channel is not None:
                routed = RoutedLine(line=line, channel=default_channel)
                result.channels.setdefault(default_channel, []).append(routed)
            else:
                result.unrouted.append(line)

    return result


def format_routed(result: RouteResult, show_unrouted: bool = True) -> List[str]:
    """Render a :class:`RouteResult` as human-readable lines.

    Each channel is printed as a header followed by its lines.  Unrouted
    lines are appended at the end when *show_unrouted* is ``True``.
    """
    out: List[str] = []

    for channel in result.channel_names():
        routed_lines = result.get(channel)
        out.append(f"[{channel}] ({len(routed_lines)} lines)")
        for rl in routed_lines:
            prefix = f"  #{rl.line_number}" if rl.line_number is not None else " "
            out.append(f"{prefix}  {rl.line.message}")

    if show_unrouted and result.unrouted:
        out.append(f"[unrouted] ({len(result.unrouted)} lines)")
        for line in result.unrouted:
            prefix = f"  #{line.line_number}" if line.line_number is not None else " "
            out.append(f"{prefix}  {line.message}")

    return out

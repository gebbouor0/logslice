"""Receive log lines from various input sources into a normalised stream."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, IO, Iterable, Iterator, List, Optional

from logslice.parser import LogLine, parse_line


@dataclass
class ReceiveResult:
    lines: List[LogLine] = field(default_factory=list)
    source_name: str = "stdin"
    skipped: int = 0

    def __len__(self) -> int:
        return len(self.lines)

    def __iter__(self) -> Iterator[LogLine]:
        return iter(self.lines)


def receive_from_stream(
    stream: IO[str],
    source_name: str = "stream",
    predicate: Optional[Callable[[LogLine], bool]] = None,
) -> ReceiveResult:
    """Read text lines from *stream*, parse each, optionally filter."""
    result = ReceiveResult(source_name=source_name)
    for i, raw in enumerate(stream, start=1):
        raw = raw.rstrip("\n")
        if not raw:
            result.skipped += 1
            continue
        log_line = parse_line(raw, line_number=i)
        if predicate is not None and not predicate(log_line):
            result.skipped += 1
            continue
        result.lines.append(log_line)
    return result


def receive_from_iterable(
    iterable: Iterable[str],
    source_name: str = "iterable",
    predicate: Optional[Callable[[LogLine], bool]] = None,
) -> ReceiveResult:
    """Parse an iterable of raw strings into LogLines."""
    result = ReceiveResult(source_name=source_name)
    for i, raw in enumerate(iterable, start=1):
        raw = raw.rstrip("\n")
        if not raw:
            result.skipped += 1
            continue
        log_line = parse_line(raw, line_number=i)
        if predicate is not None and not predicate(log_line):
            result.skipped += 1
            continue
        result.lines.append(log_line)
    return result


def receive_lines(
    source: IO[str] | Iterable[str],
    source_name: str = "stdin",
    predicate: Optional[Callable[[LogLine], bool]] = None,
) -> ReceiveResult:
    """Unified receive: accepts a stream or any iterable of raw strings."""
    if hasattr(source, "read"):
        return receive_from_stream(source, source_name=source_name, predicate=predicate)  # type: ignore[arg-type]
    return receive_from_iterable(source, source_name=source_name, predicate=predicate)  # type: ignore[arg-type]

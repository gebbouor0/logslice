"""Emit log lines to various output sinks (stdout, file, callback)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, IO, Iterable, List, Optional

from logslice.parser import LogLine


@dataclass
class EmitResult:
    emitted: List[LogLine] = field(default_factory=list)
    sink_name: str = "stdout"

    def __len__(self) -> int:
        return len(self.emitted)

    def __iter__(self):
        return iter(self.emitted)


def emit_to_stream(
    lines: Iterable[LogLine],
    stream: IO[str],
    formatter: Optional[Callable[[LogLine], str]] = None,
    sink_name: str = "stream",
) -> EmitResult:
    """Write each line to *stream*, returning an EmitResult."""
    if formatter is None:
        formatter = lambda ln: ln.raw

    result = EmitResult(sink_name=sink_name)
    for line in lines:
        stream.write(formatter(line) + "\n")
        result.emitted.append(line)
    return result


def emit_to_callback(
    lines: Iterable[LogLine],
    callback: Callable[[LogLine], None],
    sink_name: str = "callback",
) -> EmitResult:
    """Call *callback* for every line and collect them in an EmitResult."""
    result = EmitResult(sink_name=sink_name)
    for line in lines:
        callback(line)
        result.emitted.append(line)
    return result


def emit_lines(
    lines: Iterable[LogLine],
    stream: Optional[IO[str]] = None,
    callback: Optional[Callable[[LogLine], None]] = None,
    formatter: Optional[Callable[[LogLine], str]] = None,
    sink_name: str = "stdout",
) -> EmitResult:
    """Unified entry point: emit to stream and/or callback."""
    import sys

    target_stream = stream if stream is not None else sys.stdout
    collected: List[LogLine] = list(lines)

    if formatter is None:
        formatter = lambda ln: ln.raw

    result = EmitResult(sink_name=sink_name)
    for line in collected:
        target_stream.write(formatter(line) + "\n")
        if callback is not None:
            callback(line)
        result.emitted.append(line)
    return result

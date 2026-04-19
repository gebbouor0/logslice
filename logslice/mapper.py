"""Map log lines through a transformation function or field extraction."""
from dataclasses import dataclass, field
from typing import Callable, List, Optional, Any
from logslice.parser import LogLine


@dataclass
class MappedLine:
    original: LogLine
    value: Any

    @property
    def raw(self) -> str:
        return self.original.raw

    @property
    def line_number(self) -> int:
        return self.original.line_number


@dataclass
class MapResult:
    lines: List[MappedLine] = field(default_factory=list)

    def values(self) -> List[Any]:
        return [ml.value for ml in self.lines]

    def __len__(self) -> int:
        return len(self.lines)


def map_lines(lines: List[LogLine], fn: Callable[[LogLine], Any]) -> MapResult:
    """Apply fn to each line and collect results."""
    mapped = [MappedLine(original=line, value=fn(line)) for line in lines]
    return MapResult(lines=mapped)


def map_field(lines: List[LogLine], field_name: str) -> MapResult:
    """Extract a named attribute from each LogLine."""
    def extractor(line: LogLine) -> Optional[Any]:
        return getattr(line, field_name, None)
    return map_lines(lines, extractor)


def format_mapped(result: MapResult, sep: str = " => ") -> List[str]:
    """Format mapped lines as 'raw => value' strings."""
    out = []
    for ml in result.lines:
        out.append(f"{ml.raw}{sep}{ml.value}")
    return out

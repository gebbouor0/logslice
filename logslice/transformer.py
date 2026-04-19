"""Transform log line messages using a pipeline of functions."""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Callable, Optional
from logslice.parser import LogLine


TransformFn = Callable[[str], str]


@dataclass
class TransformedLine:
    original: LogLine
    message: str

    @property
    def raw(self) -> str:
        return self.original.raw

    @property
    def line_number(self) -> Optional[int]:
        return self.original.line_number


def apply_transforms(message: str, fns: List[TransformFn]) -> str:
    for fn in fns:
        message = fn(message)
    return message


def transform_lines(lines: List[LogLine], fns: List[TransformFn]) -> List[TransformedLine]:
    return [TransformedLine(original=line, message=apply_transforms(line.message, fns)) for line in lines]


def format_transformed(lines: List[TransformedLine]) -> str:
    return "\n".join(f"{t.line_number or '?':>4}: {t.message}" for t in lines)


# Built-in transforms
def strip_whitespace(msg: str) -> str:
    return msg.strip()


def to_uppercase(msg: str) -> str:
    return msg.upper()


def to_lowercase(msg: str) -> str:
    return msg.lower()


def remove_ansi(msg: str) -> str:
    import re
    return re.sub(r"\x1b\[[0-9;]*m", "", msg)


def replace_text(old: str, new: str) -> TransformFn:
    def _fn(msg: str) -> str:
        return msg.replace(old, new)
    return _fn

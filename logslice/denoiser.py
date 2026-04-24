"""Denoiser: suppress repetitive or low-signal log lines based on frequency."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Iterable, List, Optional

from logslice.parser import LogLine


@dataclass
class DenoiseResult:
    kept: List[LogLine] = field(default_factory=list)
    suppressed: List[LogLine] = field(default_factory=list)
    noise_patterns: Counter = field(default_factory=Counter)

    def __len__(self) -> int:
        return len(self.kept)

    @property
    def total_input(self) -> int:
        return len(self.kept) + len(self.suppressed)

    @property
    def suppression_rate(self) -> float:
        if self.total_input == 0:
            return 0.0
        return len(self.suppressed) / self.total_input


def _fingerprint(message: str) -> str:
    """Collapse digits and punctuation runs to produce a stable pattern key."""
    import re
    msg = re.sub(r'\d+', 'N', message)
    msg = re.sub(r'\s+', ' ', msg)
    return msg.strip().lower()


def denoise_lines(
    lines: Iterable[LogLine],
    threshold: int = 3,
    window: int = 50,
) -> DenoiseResult:
    """Suppress lines whose fingerprint appears more than *threshold* times
    within the last *window* lines.

    Args:
        lines: Input log lines.
        threshold: Max allowed occurrences within the window before suppression.
        window: Rolling window size (number of lines) for frequency counting.
    """
    if threshold < 1:
        raise ValueError("threshold must be >= 1")
    if window < 1:
        raise ValueError("window must be >= 1")

    result = DenoiseResult()
    recent: List[str] = []

    for line in lines:
        fp = _fingerprint(line.message)
        window_counts: Counter = Counter(recent)
        if window_counts[fp] >= threshold:
            result.suppressed.append(line)
            result.noise_patterns[fp] += 1
        else:
            result.kept.append(line)
        recent.append(fp)
        if len(recent) > window:
            recent.pop(0)

    return result


def format_denoised(result: DenoiseResult) -> str:
    lines = [f"[{i + 1}] {l.message}" for i, l in enumerate(result.kept)]
    lines.append(f"--- suppressed {len(result.suppressed)} noisy lines ---")
    return "\n".join(lines)

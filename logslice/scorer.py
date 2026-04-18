"""Score log lines by relevance based on pattern weights."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import re
from logslice.parser import LogLine


@dataclass
class ScoredLine:
    log_line: LogLine
    score: float
    matched_rules: List[str] = field(default_factory=list)

    @property
    def raw(self) -> str:
        return self.log_line.raw

    @property
    def line_number(self) -> Optional[int]:
        return self.log_line.line_number


@dataclass
class ScoreResult:
    lines: List[ScoredLine]
    max_score: float
    min_score: float

    def top(self, n: int) -> List[ScoredLine]:
        return sorted(self.lines, key=lambda x: x.score, reverse=True)[:n]

    def above(self, threshold: float) -> List[ScoredLine]:
        return [l for l in self.lines if l.score >= threshold]


def score_lines(
    lines: List[LogLine],
    rules: Dict[str, float],
    case_sensitive: bool = False,
) -> ScoreResult:
    """Score each line by summing weights of matching pattern rules."""
    flags = 0 if case_sensitive else re.IGNORECASE
    compiled = {pat: (re.compile(pat, flags), weight) for pat, weight in rules.items()}

    scored: List[ScoredLine] = []
    for log_line in lines:
        total = 0.0
        matched: List[str] = []
        for pat, (rx, weight) in compiled.items():
            if rx.search(log_line.message):
                total += weight
                matched.append(pat)
        scored.append(ScoredLine(log_line=log_line, score=total, matched_rules=matched))

    scores = [s.score for s in scored]
    return ScoreResult(
        lines=scored,
        max_score=max(scores) if scores else 0.0,
        min_score=min(scores) if scores else 0.0,
    )

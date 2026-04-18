"""Tests for logslice.stats module."""

from datetime import datetime

import pytest

from logslice.parser import LogLine
from logslice.stats import LogStats, compute_stats, _extract_level


def make_line(raw: str, ts: datetime | None = None, n: int = 1) -> LogLine:
    return LogLine(raw=raw, timestamp=ts, line_number=n)


DT1 = datetime(2024, 1, 1, 10, 0, 0)
DT2 = datetime(2024, 1, 1, 11, 0, 0)
DT3 = datetime(2024, 1, 1, 12, 0, 0)


def test_compute_stats_counts():
    all_lines = [make_line("INFO hello", DT1, 1), make_line("DEBUG world", DT2, 2)]
    matched = [make_line("INFO hello", DT1, 1)]
    stats = compute_stats(all_lines, matched)
    assert stats.total == 2
    assert stats.matched == 1


def test_compute_stats_levels():
    matched = [
        make_line("ERROR something broke", DT1, 1),
        make_line("ERROR again", DT2, 2),
        make_line("INFO ok", DT3, 3),
    ]
    stats = compute_stats(matched, matched)
    assert stats.levels["ERROR"] == 2
    assert stats.levels["INFO"] == 1


def test_compute_stats_timestamps():
    all_lines = [
        make_line("a", DT1, 1),
        make_line("b", DT3, 2),
        make_line("c", DT2, 3),
    ]
    stats = compute_stats(all_lines, [])
    assert stats.earliest == DT1.isoformat()
    assert stats.latest == DT3.isoformat()


def test_compute_stats_no_timestamps():
    all_lines = [make_line("no ts here", None, 1)]
    stats = compute_stats(all_lines, [])
    assert stats.earliest is None
    assert stats.latest is None


def test_extract_level_known():
    line = make_line("2024-01-01 WARN disk space low")
    assert _extract_level(line) == "WARN"


def test_extract_level_unknown():
    line = make_line("some random message")
    assert _extract_level(line) is None


def test_summary_output():
    stats = LogStats(total=10, matched=4, earliest="2024-01-01T10:00:00", latest="2024-01-01T12:00:00")
    stats.levels["ERROR"] = 2
    summary = stats.summary()
    assert "Total lines" in summary
    assert "Matched" in summary
    assert "ERROR=2" in summary
    assert "2024-01-01T10:00:00" in summary

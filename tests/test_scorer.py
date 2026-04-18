"""Tests for logslice.scorer."""
import pytest
from datetime import datetime
from logslice.parser import LogLine
from logslice.scorer import score_lines, ScoredLine, ScoreResult


def make_line(msg: str, ln: int = 1) -> LogLine:
    return LogLine(raw=msg, message=msg, timestamp=None, level=None, line_number=ln)


RULES = {"error": 10.0, "timeout": 5.0, "warn": 2.0}


def test_score_basic_match():
    lines = [make_line("connection error occurred")]
    result = score_lines(lines, RULES)
    assert result.lines[0].score == 10.0
    assert "error" in result.lines[0].matched_rules


def test_score_multiple_matches():
    lines = [make_line("error and timeout happened")]
    result = score_lines(lines, RULES)
    assert result.lines[0].score == 15.0
    assert set(result.lines[0].matched_rules) == {"error", "timeout"}


def test_score_no_match():
    lines = [make_line("everything is fine")]
    result = score_lines(lines, RULES)
    assert result.lines[0].score == 0.0
    assert result.lines[0].matched_rules == []


def test_score_case_insensitive_default():
    lines = [make_line("ERROR in service")]
    result = score_lines(lines, RULES)
    assert result.lines[0].score == 10.0


def test_score_case_sensitive():
    lines = [make_line("ERROR in service")]
    result = score_lines(lines, RULES, case_sensitive=True)
    assert result.lines[0].score == 0.0


def test_score_result_max_min():
    lines = [make_line("error timeout"), make_line("warn only"), make_line("nothing")]
    result = score_lines(lines, RULES)
    assert result.max_score == 15.0
    assert result.min_score == 0.0


def test_score_result_top():
    lines = [make_line("error"), make_line("warn"), make_line("nothing")]
    result = score_lines(lines, RULES)
    top = result.top(2)
    assert len(top) == 2
    assert top[0].score >= top[1].score


def test_score_result_above_threshold():
    lines = [make_line("error"), make_line("warn"), make_line("nothing")]
    result = score_lines(lines, RULES)
    above = result.above(5.0)
    assert all(l.score >= 5.0 for l in above)


def test_score_empty_lines():
    result = score_lines([], RULES)
    assert result.lines == []
    assert result.max_score == 0.0
    assert result.min_score == 0.0


def test_score_empty_rules():
    lines = [make_line("error critical")]
    result = score_lines(lines, {})
    assert result.lines[0].score == 0.0


def test_scored_line_properties():
    line = make_line("test message", ln=42)
    result = score_lines([line], RULES)
    sl = result.lines[0]
    assert sl.raw == "test message"
    assert sl.line_number == 42

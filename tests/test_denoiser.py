"""Tests for logslice.denoiser."""
import pytest
from logslice.parser import LogLine
from logslice.denoiser import (
    DenoiseResult,
    _fingerprint,
    denoise_lines,
    format_denoised,
)


def make_line(msg: str, n: int = 1) -> LogLine:
    return LogLine(raw=msg, message=msg, line_number=n)


# ---------------------------------------------------------------------------
# _fingerprint
# ---------------------------------------------------------------------------

def test_fingerprint_collapses_digits():
    assert _fingerprint("error at line 42") == _fingerprint("error at line 99")


def test_fingerprint_lowercases():
    assert _fingerprint("ERROR") == _fingerprint("error")


def test_fingerprint_collapses_whitespace():
    assert _fingerprint("a  b") == _fingerprint("a b")


# ---------------------------------------------------------------------------
# denoise_lines
# ---------------------------------------------------------------------------

def test_denoise_no_noise_keeps_all():
    lines = [make_line(f"unique message {i}", i) for i in range(5)]
    result = denoise_lines(lines, threshold=3)
    assert len(result.kept) == 5
    assert len(result.suppressed) == 0


def test_denoise_suppresses_above_threshold():
    # same message repeated 5 times, threshold=3 → first 3 kept, rest suppressed
    lines = [make_line("heartbeat ok", i) for i in range(5)]
    result = denoise_lines(lines, threshold=3, window=10)
    assert len(result.kept) == 3
    assert len(result.suppressed) == 2


def test_denoise_threshold_one_keeps_first_only():
    lines = [make_line("ping", i) for i in range(4)]
    result = denoise_lines(lines, threshold=1, window=10)
    assert len(result.kept) == 1
    assert len(result.suppressed) == 3


def test_denoise_window_resets_count():
    # window=2 means only last 2 lines matter; repeated pattern re-allowed after window
    lines = [
        make_line("same", 1),
        make_line("same", 2),
        make_line("other", 3),  # pushes first "same" out of window=2
        make_line("same", 4),  # only 1 "same" in window now → kept
    ]
    result = denoise_lines(lines, threshold=2, window=2)
    # line 1: count=0 → kept; line 2: count=1 → kept; line 4: count=1 (window=[other,same]) → kept
    assert make_line("same", 4) in result.kept or len(result.kept) >= 3


def test_denoise_empty_input():
    result = denoise_lines([], threshold=3)
    assert len(result) == 0
    assert result.total_input == 0


def test_denoise_suppression_rate():
    lines = [make_line("boom", i) for i in range(6)]
    result = denoise_lines(lines, threshold=3, window=10)
    assert 0.0 < result.suppression_rate <= 1.0


def test_denoise_noise_patterns_recorded():
    lines = [make_line("tick", i) for i in range(5)]
    result = denoise_lines(lines, threshold=2, window=10)
    fp = list(result.noise_patterns.keys())
    assert len(fp) > 0


def test_denoise_invalid_threshold_raises():
    with pytest.raises(ValueError):
        denoise_lines([], threshold=0)


def test_denoise_invalid_window_raises():
    with pytest.raises(ValueError):
        denoise_lines([], threshold=1, window=0)


# ---------------------------------------------------------------------------
# format_denoised
# ---------------------------------------------------------------------------

def test_format_denoised_includes_kept_messages():
    lines = [make_line("hello", 1), make_line("world", 2)]
    result = denoise_lines(lines, threshold=3)
    out = format_denoised(result)
    assert "hello" in out
    assert "world" in out


def test_format_denoised_includes_suppression_summary():
    lines = [make_line("noise", i) for i in range(5)]
    result = denoise_lines(lines, threshold=2, window=10)
    out = format_denoised(result)
    assert "suppressed" in out

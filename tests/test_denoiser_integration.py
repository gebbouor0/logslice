"""Integration tests for logslice.denoiser."""
from logslice.parser import LogLine
from logslice.denoiser import denoise_lines, format_denoised


def make_line(msg: str, n: int = 1) -> LogLine:
    return LogLine(raw=msg, message=msg, line_number=n)


def _mixed_lines():
    """Interleave noisy heartbeat lines with unique error lines."""
    lines = []
    for i in range(12):
        lines.append(make_line("heartbeat ok", i * 2))
        lines.append(make_line(f"error code {i}", i * 2 + 1))
    return lines


def test_total_lines_preserved():
    lines = _mixed_lines()
    result = denoise_lines(lines, threshold=3, window=20)
    assert result.total_input == len(lines)


def test_unique_lines_never_suppressed():
    lines = _mixed_lines()
    result = denoise_lines(lines, threshold=3, window=20)
    # each "error code N" is unique → all should be kept
    kept_msgs = {l.message for l in result.kept}
    for i in range(12):
        assert f"error code {i}" in kept_msgs


def test_noisy_lines_partially_suppressed():
    lines = _mixed_lines()
    result = denoise_lines(lines, threshold=3, window=20)
    suppressed_msgs = [l.message for l in result.suppressed]
    assert any("heartbeat" in m for m in suppressed_msgs)


def test_format_integration_no_error():
    lines = _mixed_lines()
    result = denoise_lines(lines, threshold=3, window=20)
    out = format_denoised(result)
    assert isinstance(out, str)
    assert len(out) > 0


def test_high_threshold_keeps_everything():
    lines = [make_line("same", i) for i in range(5)]
    result = denoise_lines(lines, threshold=100, window=200)
    assert len(result.kept) == 5
    assert len(result.suppressed) == 0

"""Integration tests for scanner: combines scan_lines + format_scan end-to-end."""
from logslice.parser import LogLine
from logslice.scanner import scan_lines, format_scan


def make_line(msg: str, lineno: int = 1) -> LogLine:
    return LogLine(raw=msg, message=msg, timestamp=None, line_number=lineno)


def test_scan_then_format_non_empty():
    lines = [
        make_line("ERROR connection refused", 1),
        make_line("INFO server started", 2),
        make_line("ERROR timeout", 3),
    ]
    result = scan_lines(lines, r"error")
    out = format_scan(result)
    text = "\n".join(out)
    assert "2" in text  # total matches
    assert "ERROR connection refused" in text
    assert "ERROR timeout" in text
    assert "INFO server started" not in text


def test_scan_all_lines_match():
    lines = [make_line(f"ERROR {i}", i) for i in range(5)]
    result = scan_lines(lines, r"error")
    assert result.total_matches == 5
    assert result.hit_rate == 1.0


def test_scan_no_lines_match_format_safe():
    lines = [make_line("INFO ok", i) for i in range(3)]
    result = scan_lines(lines, r"error")
    out = format_scan(result)
    # Should not raise; separator should be last line
    assert any("-" * 10 in l for l in out)
    assert result.total_matches == 0


def test_scan_multispan_format_shows_count():
    lines = [make_line("retry retry retry", 1)]
    result = scan_lines(lines, r"retry")
    out = format_scan(result)
    combined = "\n".join(out)
    assert "(3x)" in combined

"""Integration tests: censor + filter/format pipeline."""
from logslice.parser import LogLine
from logslice.censor import censor_lines, format_censor
from logslice.filter import filter_lines


def make_line(msg: str, n: int = 1, level: str = "INFO") -> LogLine:
    ll = LogLine(raw=msg, line_number=n)
    ll.message = msg
    ll.timestamp = None
    ll.level = level
    return ll


def _mixed_lines():
    return [
        make_line("user 10.0.0.1 login ok", 1, "INFO"),
        make_line("error from 10.0.0.2 crash", 2, "ERROR"),
        make_line("all clear", 3, "INFO"),
        make_line("admin@corp.com signed in", 4, "INFO"),
        make_line("fatal 10.0.0.3 unreachable", 5, "ERROR"),
    ]


def test_censor_then_format_length_matches_input():
    lines = _mixed_lines()
    result = censor_lines(lines, categories=["ip", "email"])
    out = format_censor(result)
    assert len(out) == len(lines)


def test_censor_removes_ips_from_all_lines():
    lines = _mixed_lines()
    result = censor_lines(lines, categories=["ip"])
    for cl in result.lines:
        import re
        assert not re.search(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", cl.message)


def test_censor_total_input_preserved():
    lines = _mixed_lines()
    result = censor_lines(lines, categories=["ip"])
    assert result.total_input == len(lines)


def test_censor_then_as_log_line_filterable():
    """Censored lines converted back to LogLine can be filtered by pattern."""
    lines = _mixed_lines()
    result = censor_lines(lines, categories=["ip"])
    log_lines = [cl.as_log_line() for cl in result.lines]
    # IPs replaced — searching for original IP should yield nothing
    matched = [ll for ll in log_lines if "10.0.0.1" in (ll.message or "")]
    assert matched == []


def test_censor_only_flagged_lines_have_categories_hit():
    lines = _mixed_lines()
    result = censor_lines(lines, categories=["ip", "email"])
    for cl in result.lines:
        if not cl.was_censored:
            assert cl.categories_hit == []
        else:
            assert len(cl.categories_hit) >= 1

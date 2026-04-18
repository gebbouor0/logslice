import pytest
from datetime import datetime
from logslice.parser import LogLine
from logslice.tagger import (
    tag_line,
    tag_lines,
    filter_by_tag,
    format_tagged,
    TaggedLine,
)


def make_line(raw: str, line_number: int = 1) -> LogLine:
    return LogLine(raw=raw, timestamp=None, message=raw, line_number=line_number)


RULES = {
    "error": r"ERROR",
    "timeout": r"timeout",
    "db": r"database|db",
}


def test_tag_line_single_match():
    line = make_line("ERROR: something went wrong")
    result = tag_line(line, RULES)
    assert "error" in result.tags
    assert "timeout" not in result.tags


def test_tag_line_multiple_matches():
    line = make_line("ERROR: database timeout")
    result = tag_line(line, RULES)
    assert "error" in result.tags
    assert "timeout" in result.tags
    assert "db" in result.tags


def test_tag_line_no_match():
    line = make_line("INFO: all good")
    result = tag_line(line, RULES)
    assert result.tags == []


def test_tag_lines_count():
    lines = [make_line("ERROR: oops", i) for i in range(5)]
    results = tag_lines(lines, RULES)
    assert len(results) == 5
    assert all("error" in r.tags for r in results)


def test_filter_by_tag_returns_matching():
    lines = [
        make_line("ERROR: bad", 1),
        make_line("INFO: fine", 2),
        make_line("ERROR: also bad", 3),
    ]
    tagged = tag_lines(lines, RULES)
    errors = filter_by_tag(tagged, "error")
    assert len(errors) == 2


def test_filter_by_tag_empty_result():
    lines = [make_line("INFO: fine", 1)]
    tagged = tag_lines(lines, RULES)
    result = filter_by_tag(tagged, "error")
    assert result == []


def test_format_tagged_with_tags():
    line = make_line("ERROR: boom")
    tl = TaggedLine(log_line=line, tags=["error", "db"])
    out = format_tagged(tl)
    assert out.startswith("[")
    assert "error" in out
    assert "db" in out
    assert "ERROR: boom" in out


def test_format_tagged_no_tags():
    line = make_line("INFO: ok")
    tl = TaggedLine(log_line=line, tags=[])
    out = format_tagged(tl)
    assert out.startswith("[]")
    assert "INFO: ok" in out


def test_tagged_line_raw_and_line_number():
    line = make_line("DEBUG: test", line_number=42)
    tl = TaggedLine(log_line=line, tags=["x"])
    assert tl.raw == "DEBUG: test"
    assert tl.line_number == 42

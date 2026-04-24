"""Integration tests: marker combined with filter and formatter."""
from logslice.parser import LogLine
from logslice.marker import mark_lines, format_marked
from logslice.filter import filter_lines


def make_line(msg: str, n: int = 1) -> LogLine:
    return LogLine(raw=msg, message=msg, line_number=n, timestamp=None, level=None)


def test_mark_after_filter_only_errors_marked():
    lines = [
        make_line("INFO start", 1),
        make_line("ERROR crash", 2),
        make_line("INFO end", 3),
    ]
    filtered = filter_lines(lines, pattern="ERROR")
    result = mark_lines(filtered, predicate=lambda l: "ERROR" in l.message, marker="ERR")
    assert all(ml.marker == "ERR" for ml in result.lines)


def test_mark_first_and_last_on_filtered_set():
    lines = [make_line(f"INFO msg{i}", i) for i in range(10)]
    filtered = filter_lines(lines, pattern="INFO")
    result = mark_lines(
        filtered,
        predicate=lambda _: False,
        mark_first=True,
        mark_last=True,
    )
    assert result.lines[0].marker == "first"
    assert result.lines[-1].marker == "last"


def test_format_output_lines_count_matches_input():
    lines = [make_line(f"line {i}", i) for i in range(7)]
    result = mark_lines(lines, predicate=lambda _: False, every_nth=3)
    out = format_marked(result)
    assert len(out) == 7


def test_marked_lines_preserve_raw():
    lines = [make_line("raw content here", 5)]
    result = mark_lines(lines, predicate=lambda _: True)
    assert result.lines[0].raw == "raw content here"
    assert result.lines[0].line_number == 5
